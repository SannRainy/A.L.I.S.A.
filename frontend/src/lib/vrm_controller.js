import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

export class VRMController {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.currentVrm = null;
        this.loader = new GLTFLoader();
        this.loader.register((parser) => new VRMLoaderPlugin(parser));
        
        this.isLoading = false;
        this.loadingMesh = null;
        this.loadingSegments = [];
        
        this.mouseTarget = new THREE.Vector2(0, 0);
        this.currentMouse = new THREE.Vector2(0, 0);
        this.eyeTarget = new THREE.Vector2(0, 0);

        this.seeds = { head: Math.random() * 100, sway: Math.random() * 100, eye: Math.random() * 100 };
        this.blinkTimer = 0;
        this.isBlinking = false;
        this.nextBlinkTime = 0;
        this.initBlinkTimer();

        // Lip Sync State
        this.isSpeaking = false;
        this.speakTimer = 0;
        this.vowels = ['aa', 'ih', 'ou', 'ee', 'oh'];
        this.currentVowelTarget = null;
        
        // Target & Current Expressions for Smooth Damp
        this.targetExpressions = {};
        this.currentExpressions = {};
        const expressionKeys = ['aa', 'ih', 'ou', 'ee', 'oh', 'blink', 'happy', 'relaxed', 'neutral'];
        expressionKeys.forEach(k => {
            this.targetExpressions[k] = 0;
            this.currentExpressions[k] = 0;
        });
    }

    async loadModel(url) {
        return new Promise((resolve, reject) => {
            this.loader.load(url, (gltf) => {
                const vrm = gltf.userData.vrm;
                if (!vrm) {
                    reject(new Error("VRM instance tidak ditemukan di GLTF"));
                    return;
                }

                // Rotasi yang aman untuk model
                VRMUtils.rotateVRM0(vrm);
                
                this.currentVrm = vrm;
                this.scene.add(vrm.scene);

                // SCALE ADJUSTED (2.8 instead of 3.5)
                vrm.scene.scale.set(2.8, 2.8, 2.8); 
                vrm.scene.position.set(0, -1, 0); 
                
                vrm.scene.traverse((obj) => { 
                    if (obj.isMesh) {
                        obj.frustumCulled = false; 
                        obj.castShadow = true;
                        obj.receiveShadow = true;

                        const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
                        mats.forEach((mat) => {
                            if (mat.isMToonMaterial) {
                                if (mat.outlineWidthMode !== undefined) {
                                    mat.outlineWidthMode = 'screenCoordinates';
                                    mat.outlineWidth = 0.003;
                                    mat.outlineColorFactor.set(0, 0, 0);
                                } else {
                                    mat.outlineWidthFactor = 0.003;
                                    if (mat.outlineColorFactor) mat.outlineColorFactor.setHex(0x000000);
                                }
                            }
                        });
                    }
                });

                if (vrm.humanoid) {
                    const leftArm = vrm.humanoid.getNormalizedBoneNode('leftUpperArm');
                    const rightArm = vrm.humanoid.getNormalizedBoneNode('rightUpperArm');
                    
                    if (leftArm) leftArm.rotation.z = -1.2; 
                    if (rightArm) rightArm.rotation.z = 1.2;
                }

                if (this.isLoading) {
                    this.setLoading(true);
                }

                resolve(vrm);
            }, undefined, reject);
        });
    }

    initBlinkTimer() { 
        this.nextBlinkTime = Date.now() + 2000 + Math.random() * 5000; 
    }

    updateMouse(x, y) {
        this.mouseTarget.set(x, y);
    }

    update(delta, time) {
        if (!this.currentVrm) return;

        this.updateBlinking(delta);
        this.updateSpeaking(delta);
        
        if (this.isLoading && this.loadingMesh) {
            if (this.loadingSegments && this.loadingSegments.length > 0) {
                const numSegments = this.loadingSegments.length;
                const speed = 1.5; // Cycles per second
                const activeIndex = Math.floor((time * speed * numSegments) % numSegments);
                
                for (let i = 0; i < numSegments; i++) {
                    const diff = (activeIndex - i + numSegments) % numSegments;
                    // Fades from 1.0 (leading segment) down to 0.12 (trailing segments)
                    const opacity = Math.max(0.12, 1.0 - (diff / numSegments) * 0.9);
                    this.loadingSegments[i].material.opacity = opacity;
                }
            }
            
            // Keep static scale to prevent front-to-back bouncing/clipping
            this.loadingMesh.scale.set(1.0, 1.0, 1.0);
        }
        
        this.currentMouse.lerp(this.mouseTarget, delta * 3.0);
        
        const eyeMicroX = Math.sin(time * 2.0 + this.seeds.eye) * 0.05;
        const eyeMicroY = Math.cos(time * 3.0 + this.seeds.eye) * 0.05;
        const noisyEyeTarget = this.mouseTarget.clone().add(new THREE.Vector2(eyeMicroX, eyeMicroY));
        this.eyeTarget.lerp(noisyEyeTarget, delta * 8.0);
        
        this.applyManualTracking(time);
        this.applyExpressions(delta);

        this.currentVrm.update(delta);
    }

    applyManualTracking(time) {
        if (!this.currentVrm.humanoid) return;

        const neck = this.currentVrm.humanoid.getNormalizedBoneNode('neck');
        const head = this.currentVrm.humanoid.getNormalizedBoneNode('head');
        const chest = this.currentVrm.humanoid.getNormalizedBoneNode('chest');
        const spine = this.currentVrm.humanoid.getNormalizedBoneNode('spine');
        const hips = this.currentVrm.humanoid.getNormalizedBoneNode('hips');
        const leftShoulder = this.currentVrm.humanoid.getNormalizedBoneNode('leftShoulder');
        const rightShoulder = this.currentVrm.humanoid.getNormalizedBoneNode('rightShoulder');
        const leftEye = this.currentVrm.humanoid.getNormalizedBoneNode('leftEye');
        const rightEye = this.currentVrm.humanoid.getNormalizedBoneNode('rightEye');

        const breathing = Math.sin(time * 1.5);
        if (chest) {
            chest.scale.set(1 + breathing * 0.01, 1 + breathing * 0.01, 1 + breathing * 0.02);
            chest.rotation.x = breathing * 0.005;
        }

        const swayX = Math.cos(time * 0.5 + this.seeds.sway) * 0.01;
        const swayY = Math.sin(time * 0.4 + this.seeds.sway) * 0.01;
        
        if (hips) {
            hips.rotation.y = swayY;
            hips.rotation.z = swayX;
        }

        if (spine) {
            spine.rotation.x = Math.sin(time * 0.5) * 0.01;
            spine.rotation.z = swayX * 0.5;
        }

        if (leftShoulder) leftShoulder.rotation.z = breathing * 0.01;
        if (rightShoulder) rightShoulder.rotation.z = -breathing * 0.01;

        const clamp = (val, min, max) => Math.max(min, Math.min(max, val));

        const targetRotX = clamp(-this.currentMouse.y * 0.15, -0.2, 0.2);
        const targetRotY = clamp(this.currentMouse.x * 0.25, -0.4, 0.4);
        
        if (neck) {
            neck.rotation.x = targetRotX * 0.4;
            neck.rotation.y = targetRotY * 0.4;
        }
        
        if (head) {
            head.rotation.x = targetRotX * 0.6 + Math.cos(time * 0.8 + this.seeds.head) * 0.005;
            head.rotation.y = targetRotY * 0.6 + Math.sin(time * 1.1 + this.seeds.head) * 0.005;
            head.rotation.z = targetRotY * -0.1;
        }

        if (leftEye && rightEye) {
            const eyeRotX = clamp(-this.eyeTarget.y * 0.05, -0.1, 0.1);
            const eyeRotY = clamp(this.eyeTarget.x * 0.1, -0.15, 0.15);
            
            leftEye.rotation.x = eyeRotX;
            leftEye.rotation.y = eyeRotY;
            rightEye.rotation.x = eyeRotX;
            rightEye.rotation.y = eyeRotY;
        }
    }

    updateBlinking(delta) {
        const now = Date.now();
        if (!this.isBlinking && now > this.nextBlinkTime) { 
            this.isBlinking = true; 
            this.blinkTimer = 0; 
        }
        
        if (this.isBlinking) {
            this.blinkTimer += delta * 6;
            const val = Math.sin(this.blinkTimer * Math.PI);
            
            if (this.blinkTimer >= 1.0) {
                this.isBlinking = false;
                this.initBlinkTimer();
                this.targetExpressions['blink'] = 0;
            } else {
                this.targetExpressions['blink'] = Math.max(0, val);
            }
        }
    }

    setSpeaking(isSpeaking) {
        this.isSpeaking = isSpeaking;
        if (!isSpeaking) {
            this.vowels.forEach(v => this.targetExpressions[v] = 0);
            this.targetExpressions['happy'] = 0;
            this.targetExpressions['relaxed'] = 0;
            this.targetExpressions['neutral'] = 1;
        } else {
            this.targetExpressions['happy'] = 0.3;
            this.targetExpressions['neutral'] = 0.7;
        }
    }

    updateSpeaking(delta) {
        if (!this.isSpeaking) return;
        
        this.speakTimer += delta * 8; 
        
        if (this.speakTimer > 1.0) {
            this.speakTimer = 0;
            if (this.currentVowelTarget) {
                this.targetExpressions[this.currentVowelTarget] = 0;
            }
            if (Math.random() > 0.15) {
                this.currentVowelTarget = this.vowels[Math.floor(Math.random() * this.vowels.length)];
                this.targetExpressions[this.currentVowelTarget] = Math.random() * 0.3 + 0.2; 
            } else {
                this.currentVowelTarget = null;
            }
        }
    }

    applyExpressions(delta) {
        Object.keys(this.targetExpressions).forEach(key => {
            const speed = this.vowels.includes(key) || key === 'blink' ? 15.0 : 5.0;
            this.currentExpressions[key] += (this.targetExpressions[key] - this.currentExpressions[key]) * delta * speed;
            this.setExpressionValueRaw(key, this.currentExpressions[key]);
        });
    }

    setExpressionValueRaw(name, val) {
        if (this.currentVrm.expressionManager) {
            this.currentVrm.expressionManager.setValue(name, val);
        }
    }

    createRoundedRectShape(width, height, radius) {
        const shape = new THREE.Shape();
        const x = -width / 2;
        const y = -height / 2;
        
        shape.moveTo(x, y + radius);
        shape.lineTo(x, y + height - radius);
        shape.quadraticCurveTo(x, y + height, x + radius, y + height);
        shape.lineTo(x + width - radius, y + height);
        shape.quadraticCurveTo(x + width, y + height, x + width, y + height - radius);
        shape.lineTo(x + width, y + radius);
        shape.quadraticCurveTo(x + width, y, x + width - radius, y);
        shape.lineTo(x + radius, y);
        shape.quadraticCurveTo(x, y, x, y + radius);
        
        return shape;
    }

    createLoadingIndicator() {
        const group = new THREE.Group();
        
        const numSegments = 12;
        const radius = 0.038;
        const pillWidth = 0.0055; // Thicker pills
        const pillLength = 0.013; // Thicker pills
        const pillRadius = pillWidth / 2;
        
        this.loadingSegments = [];
        
        // Shape representing a rounded pill
        const pillShape = this.createRoundedRectShape(pillWidth, pillLength, pillRadius);
        const geom = new THREE.ShapeGeometry(pillShape);
        
        // Offset relative to head bone coordinate space:
        // X = -0.045 (Aligned right above the VRM's right eye / viewer's left side)
        // Y = 0.155 (Forehead level, slightly higher)
        // Z = 0.11 (Moved forward to float clearly in front of hair/face)
        const centerX = -0.045;
        const centerY = 0.155;
        const centerZ = 0.11;
        
        for (let i = 0; i < numSegments; i++) {
            const angle = (i / numSegments) * Math.PI * 2;
            
            // White double-sided material unique for each segment to control individual opacity
            const mat = new THREE.MeshBasicMaterial({ 
                color: 0xffffff,
                transparent: true,
                opacity: 0.1,
                side: THREE.DoubleSide
            });
            
            const mesh = new THREE.Mesh(geom, mat);
            
            // Spoke container group for clean positioning & radial orientation in X-Y plane
            const pivot = new THREE.Group();
            pivot.position.set(centerX, centerY, centerZ);
            pivot.rotation.z = angle; // rotate around Z-axis (pointing forward)
            
            // Place mesh at distance R from center along local Y-axis
            mesh.position.set(0, radius, 0);
            
            pivot.add(mesh);
            group.add(pivot);
            
            this.loadingSegments.push(mesh);
        }
        
        return group;
    }

    setLoading(isLoading) {
        this.isLoading = isLoading;
        if (isLoading) {
            if (!this.loadingMesh) {
                this.loadingMesh = this.createLoadingIndicator();
            }
            if (this.currentVrm && this.currentVrm.humanoid) {
                const head = this.currentVrm.humanoid.getNormalizedBoneNode('head');
                if (head && !head.children.includes(this.loadingMesh)) {
                    head.add(this.loadingMesh);
                }
            }
        } else {
            if (this.loadingMesh && this.loadingMesh.parent) {
                this.loadingMesh.parent.remove(this.loadingMesh);
            }
        }
    }
}
