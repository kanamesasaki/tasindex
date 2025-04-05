// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
    output: 'static',  // 静的サイト生成を使用
    outDir: './dist',  // 出力先ディレクトリを指定
    build: {
    }
  });
