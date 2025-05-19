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
  <div class="flex items-center gap-2">
    <button
      class="flex items-center gap-2.5 w-full text-xs cursor-pointer hover:text-light-green clear-button hover:bg-light-green/20 active:bg-light-green/30 bg-light-green/10 focus-visible:outline-light-green focus-visible:outline outline-offset-1 back-button"
      on:click={undoOutputImage}
    >
      <Undo size={16} />Back
    </button>

    <button
      class="flex items-center gap-2.5 w-full text-xs cursor-pointer hover:text-light-green clear-button hover:bg-light-green/20 active:bg-light-green/30 bg-light-green/10 focus-visible:outline-light-green focus-visible:outline outline-offset-1 next-button"
      on:click={redoOutputImage}
    >
      <Redo size={16} />Next
    </button>
  </div>
  <button
    class="special-button text-xs tools-container tools-container-sm yellow-background focus-visible:outline-light-green focus-visible:outline outline-offset-1"
    on:click={enhance}
  >
    <Wand size={16} />Enhance
  </button>
  <button
    class="text-xs tools-container tools-container-sm focus-visible:outline-light-green focus-visible:outline outline-offset-1"
    on:click={movetoCanvas}
  >
    <ArrowLeftSquare size={16} />Move to Canvas
  </button>

  <button
    class="text-xs tools-container tools-container-sm focus-visible:outline-light-green focus-visible:outline outline-offset-1"
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

  .back-button,
  .next-button {
    @apply flex py-2 px-3 border rounded-[10px] border-light-green/5  w-fit cursor-auto;
  }
</style>
