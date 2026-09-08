/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1B2A4A",       // deep navy — primary
        inkdark: "#101B33",   // darker navy for hover/depth
        saffron: "#E58A26",   // accent — standards/certification cues
        canvas: "#F6F7F9",    // page background (light mode)
        line: "#DDE1E8",      // borders/dividers (light mode)
        slate: "#475467",     // body text (light mode)
        slatelight: "#8892A0"
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
        heading: ["Archivo Black", "sans-serif"]
      },
      borderRadius: {
        sm: "4px",
        DEFAULT: "6px",
        lg: "10px"
      }
    },
  },
  plugins: [],
}
