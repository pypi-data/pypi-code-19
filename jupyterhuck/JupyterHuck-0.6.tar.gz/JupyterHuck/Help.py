# -*- coding: utf-8 -*-
"""
Created on Wed May  3 20:28:19 2017

@author: Yuki
"""

helpText='''
<html>
 <head>
  <title>Help</title>
 </head>
 <body>

  <h1>MyTree</h1>

  <p>A folder which contains folders or data.These are labeled 'folder' in the MyTreeWidget's 
  	Type column.You can set a working folder by double-clicking a folder on the Type column. 
  	The working folder is highlighted by pink color and can be accessd by <code>r.cur</code> (<code>r</code> is the refference 
  	to which you assigned the MyTreeWidget.)</p>
  	
  	<h2>methods</h2>

  		<ul>
   		<li><code>add(a,'name')</code></li>
   		<p>Add a to MyTree as name.If you don't specify <code>'name'</code>,the refference label itself(
   		in this case <code>'a'</code>) is regarded as the name.</p>
   		<li><code>pop('name')</code></li>
   		<p>Delete what is specified by <code>'name'</code> from MyTree and return it.</p>
   		<li><code>loadFile()</code></li>
   		<p>This method will open a file dialog.Choose a file and the data in that will be loaded 
   		to MyTree</p>
  		</ul>
  	
  <h1>MyTreeWidget</h1>
  <p>The instance of this class is what you get by the method <code>getRoot()</code>.If you assign the 
  instance to <code>r</code>,<code>r.cur</code> is the working folder highlighted by pink color.</p>
  	
  	<h2>methods</h2>
  		<ul>
  		<li><code>save()</code></li>
  		<p>Save the all data contained in MyTreeWidget to the file which you specified by <code>getRoot()</code>.
  		<code>save(True)</code> will open a file dialog and you can choose another file to save the data.</p>
  		<li><code>refresh()</code></li>
  		<p>You can use this method when something wrong happen to MyTreeWidget.This method refresh itself 
  		not breaking the data contained.</p>
  		</ul>
  		
  <h1>MyGraphWindow</h1>
  <p>This is a graph window which can be added to and handled by MyTreeWidget.</p>
  
  	<h2>methods</h2>
  		<ul>
  		<li><code>plot(*)</code></li>
  		<p>The arguments for <code>plot</code> are the same with <code>matplotlib.pyplot.plot</code>.
  		Check the other options <a href="http://matplotlib.org/api/pyplot_api.html?highlight=plot#module-matplotlib.pyplot">here:</a></p>
  		
  <hr />
  <footer>
   <address>
    Author:Yuki Arai  
    <a href="mailto:yourmail@domain.com">mail to the author</a>
   </address>
   2017 5/3 updated
  </footer>
 </body>
</html>
'''