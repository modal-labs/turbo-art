<script lang="ts">
  import {
    Undo,
    Redo,
    ArrowDownToLine,
    ArrowLeftSquare,
    Wand,
  } from "lucide-svelte";

  export let undoOutputImage: () => void;
  export let redoOutputImage: () => void;
  export let enhance: () => void;
  export let movetoCanvas: () => void;
  export let downloadImage: () => void;
</script>

<div class="flex flex-col sm:gap-3 gap-2">
  <div class="tools-container">
    <button class="text-xs flex gap-1" on:click={undoOutputImage}>
      <Undo size={16} />Back
    </button>
    <div class="w-[1px] h-4 bg-white/10" />
    <button class="text-xs flex gap-1" on:click={redoOutputImage}>
      <Redo size={16} />Next
    </button>
  </div>
  <button
    class="special-button text-xs tools-container tools-container-sm yellow-background"
    on:click={enhance}
  >
    <Wand size={16} />Enhance
  </button>
  <button
    class="text-xs tools-container tools-container-sm"
    on:click={movetoCanvas}
  >
    <ArrowLeftSquare size={16} />Move to Canvas
  </button>

  <button
    class="text-xs tools-container tools-container-sm"
    on:click={downloadImage}
  >
    <ArrowDownToLine size={16} /> Download
  </button>
</div>

<style lang="postcss">
  .tools-container,
  .tools-container-sm {
    @apply gap-1.5 px-2 min-w-[132px];
  }

  @media (min-width: 1024px) {
    .tools-container {
      @apply w-full;
    }
  }

  .yellow-background {
    @apply bg-muted-yellow text-gray-900;
  }
</style>
