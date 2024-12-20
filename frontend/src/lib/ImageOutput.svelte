<script lang="ts">
  export let imgOutput: HTMLImageElement;
  export let isFirstImageGenerated: boolean;
  export let resizeImage: (event: Event) => void;
</script>

<img
  width={320}
  height={320}
  alt="loading..."
  bind:this={imgOutput}
  class="bg-[#D9D9D9]"
  class:hidden={!isFirstImageGenerated}
  on:load={resizeImage}
/>
