<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-background flex">
    <!-- Left decorative panel -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-sidebar">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-eeg-cyan/10" />
      <!-- Animated grid -->
      <div
        class="absolute inset-0 opacity-[0.04]"
        style="background-image: linear-gradient(hsl(var(--border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border)) 1px, transparent 1px); background-size: 40px 40px;"
      />
      <div class="relative z-10 flex flex-col justify-between p-12 w-full">
        <div class="flex items-center gap-3">
          <div class="h-9 w-9 rounded-xl bg-primary/20 ring-1 ring-primary/40 flex items-center justify-center">
            <svg class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <div class="text-base font-bold text-foreground">NeuralES</div>
            <div class="text-xs text-muted-foreground">Plateforme médicale EEG</div>
          </div>
        </div>

        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-6">
            <span class="h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
            Interface clinique sécurisée
          </div>
          <h2 class="text-3xl font-bold text-foreground leading-tight mb-4">
            Analyse EEG<br />
            <span class="gradient-text">en temps réel</span>
          </h2>
          <p class="text-sm text-muted-foreground leading-relaxed max-w-sm">
            Accédez à l'acquisition de signaux cérébraux, la gestion des patients et
            l'analyse des résultats depuis une interface unifiée.
          </p>
        </div>

        <div class="flex items-center gap-6 text-xs text-muted-foreground">
          <div class="flex items-center gap-2">
            <div class="h-6 w-6 rounded-lg bg-eeg-cyan/10 flex items-center justify-center">
              <div class="h-2 w-2 rounded-full bg-eeg-cyan"></div>
            </div>
            <span>Acquisition</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="h-6 w-6 rounded-lg bg-eeg-emerald/10 flex items-center justify-center">
              <div class="h-2 w-2 rounded-full bg-eeg-emerald"></div>
            </div>
            <span>Analyse</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="h-6 w-6 rounded-lg bg-primary/10 flex items-center justify-center">
              <div class="h-2 w-2 rounded-full bg-primary"></div>
            </div>
            <span>Résultats</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: slot for login form -->
    <div class="flex-1 flex items-center justify-center px-6 py-12">
      <slot />
    </div>
  </div>
</template>
