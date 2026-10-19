/* Runs in <head> before the page paints: marks the document as script-enabled so CSS can collapse the nav
   into the Menu button only when the button will work. Without JavaScript the nav stays visible. */
document.documentElement.className += ' js';
