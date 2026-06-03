<script>
	import "../app.css";
	export let data;
	export let params;

	// Use console.debug to reference variables and avoid unused warnings
	// without affecting the component's reactivity or logic
	if (false) {
		console.debug(data, params);
	}
</script>

<slot />