/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101218",
        panel: "#151a24",
        accent: "#ff5d3d",
        electric: "#35d0ff"
      }
    }
  },
  plugins: []
};
