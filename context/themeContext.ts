// "use client";
// import { createContext, useContext, useState, useRef } from "react";

// const ThemeContext = createContext("light");

// function ThemeContextProvider({children : JSX.Element}) {
//   const [isActive, setIsActive] = useState(false);
// const html = useRef(document.documentElement)

// const toggleThemeMode = () => {
//    setIsActive(!isActive)
//    const mode = html.current.classList.toggle("dark")
//    localStorage.setItem("mode",JSON.stringify(mode))
// }

//   return (
//     <ThemeContext.Provider value={{isActive}} > {children} </ThemeContext>
//   )
// }

// const useTheme = () => {
//   return useContext(ThemeContext);
// };

// export { ThemeContextProvider, useTheme };
