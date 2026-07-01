/** Generic CSS Module type declaration for *.module.css imports */
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}
