import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
    // middlewareMode: true,
    // configureServer: (server) => {
    //   return () => {
    //     server.middlewares.use((req, res, next) => {
    //       res.removeHeader('Access-Control-Allow-Origin');
    //       next();
    //     });
    //   }
    // }
    // configureServer: (server) => {}
    }
});
