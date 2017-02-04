### Web App Explained

This code uses Flask and boostrap to generate the content used by Sifting the Overflow.

* chrome_extension contains the code for the browser extension. The .zip file is what I uploaded to the chrome store.
* static has the css files, images, and other static components of the website.
* templates is a folder with the html templates that are used to generate the web pages hosted by my aws instance.
  * this includes siftingtheoverflow.com and the pages that users are redirected to when they use Stack the Overflow.
* StackExchange_Query.py is the code (model) that runs when people use Sifting the Overflow.
* views.py is the code that controls when to run the model and what to return (the Flask code)
