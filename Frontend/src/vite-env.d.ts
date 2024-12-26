/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  // add more env variables types here if needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
