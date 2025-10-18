## To extract the information from freecodecamp.org articles

### 1. Get the link of the article : 
In the homepage of freecodecamp.org, we can find the links of the articles in the div class "post-card-title", specifically in the anchor tag <a> inside it. 

### 2. Get the article title:
In the homepage of freecodecamp.org, the article title is located inside the anchor tag <a> within the h2 tag that has the class "post-card-title".

This is an example of the html structure of the article card where we can find the title and link:
```html
<div class="post-card-content">
            <div class="post-card-content-link">
                <header class="post-card-header">
                    
                        <span class="post-card-tags">
                            <a dir="ltr" href="/news/tag/python/">
                                #Python
                            </a>
                        </span>
                    
                    <h2 class="post-card-title">
                        <a href="/news/how-to-parse-ini-config-files-in-python-with-configparser/">
                            How to Parse INI Config Files in Python with Configparser
                        </a>
                    </h2>
                </header>
            </div>
            <footer class="post-card-meta">
                
                    <ul class="author-list" data-test-label="author-list">
                        
                            
    
    
    

    <li class="author-list-item" data-test-label="author-list-item">
        <a href="/news/author/balapriyac/" class="static-avatar">
            
                
    <img srcset="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg 30w" sizes="30px" src="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg" class="author-profile-image" alt="Bala Priya C" width="1646" height="1460" onerror="this.style.display='none'" data-test-label="profile-image">
  
            
        </a>
        <span class="meta-content">
            <a class="meta-item" href="/news/author/balapriyac/" data-test-label="profile-link">
                
                    Bala Priya C
                
            </a>
            <time class="meta-item" datetime="2025-10-17T15:10:37.893Z" data-test-label="post-published-time">a day ago</time>
        </span>
    </li>

                        
                    </ul>
                
            </footer>
        </div>
```

### 3. Get the author name and article date:
The author name is located in the article page , once we extract the link of the article, we can navigate to it and find the article date and author name.The article date is located in the <time> tag with class "post-full-meta-date", and the author name is located in the <a> tag inside the section with class "author-card-name".

This is an example of the html structure of the article page where we can find the author name and article date:
``` html
<article class="post-full post">
                <header class="post-full-header">
                    <section class="post-full-meta">
                        <time class="post-full-meta-date" data-test-label="post-full-meta-date" datetime="2025-10-17T15:10:37.893Z">
                            October 17, 2025
                        </time>
                        
                            <span class="date-divider">/</span>
                            <a dir="ltr" href="/news/tag/python/">
                                #Python
                            </a>
                        
                    </section>
                    <h1 class="post-full-title" data-test-label="post-full-title">How to Parse INI Config Files in Python with Configparser</h1>
                </header>
                
                    <div class="post-full-author-header" data-test-label="author-header-no-bio">
                        
                            
    
    
    

    <section class="author-card" data-test-label="author-card">
        
            
    <img srcset="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg 60w" sizes="60px" src="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg" class="author-profile-image" alt="Bala Priya C" width="1646" height="1460" onerror="this.style.display='none'" data-test-label="profile-image">
  
        

        <section class="author-card-content author-card-content-no-bio">
            <span class="author-card-name">
                <a href="/news/author/balapriyac/" data-test-label="profile-link">
                    
                        Bala Priya C
                    
                </a>
            </span>
            
        </section>
    </section>

                        
                    </div>
                
                <figure class="post-full-image">
                    
    <picture>
      <source media="(max-width: 700px)" sizes="1px" srcset="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7 1w">
      <source media="(min-width: 701px)" sizes="(max-width: 800px) 400px, (max-width: 1170px) 700px, 1400px" srcset="https://cdn.hashnode.com/res/hashnode/image/upload/v1760712555277/4eabf2d7-fa9d-445b-8e0a-6ebdee53790c.png">
      <img onerror="this.style.display='none'" src="https://cdn.hashnode.com/res/hashnode/image/upload/v1760712555277/4eabf2d7-fa9d-445b-8e0a-6ebdee53790c.png" alt="How to Parse INI Config Files in Python with Configparser" ,="" width="600" height="400" data-test-label="feature-image">
    </picture>
  
                </figure>
                <section class="post-full-content">
                    <div class="post-and-sidebar">
                        <section class="post-content " data-test-label="post-content">
                            
<p>Configuration files provide a structured way to manage application settings that's more organized than environment variables alone.</p>
<p>INI files, short for initialization files, with their simple section-based format, are both easy to read and parse. Python's built-in <a target="_blank" href="https://docs.python.org/3/library/configparser.html">configparser module</a> makes working with these files straightforward and powerful.</p>
<p>This tutorial will teach you how to read and parse such <code>.ini</code> config files using the <code>configparser</code> module.</p>
<p>🔗 <a target="_blank" href="https://github.com/balapriyac/python-basics/tree/main/config-management-basics/parsing-ini-files"><strong>Here’s the code on GitHub</strong></a>.</p>
<h2 id="heading-prerequisites">Prerequisites</h2>
<p>To follow along with this tutorial, you should have:</p>
<ul>
<li><p>Python 3.7 or later installed on your system</p>
</li>
<li><p>Basic understanding of Python syntax and data structures (dictionaries, strings)</p>
</li>
<li><p>Familiarity with file operations in Python</p>
</li>
<li><p>A text editor or IDE for writing Python code</p>
</li>
<li><p>Basic knowledge of configuration files and why they're used in applications</p>
</li>
</ul>
<p>No external packages are required, as we'll be using Python's built-in <code>configparser</code> module.</p>
<h2 id="heading-table-of-contents">Table of Contents</h2>
<ol>
<li><p><a class="post-section-overview" href="#heading-understanding-the-ini-file-format">Understanding the INI File Format</a></p>
</li>
<li><p><a class="post-section-overview" href="#heading-basic-configparser-usage">Basic ConfigParser Usage</a></p>
</li>
<li><p><a class="post-section-overview" href="#heading-type-conversion-and-default-values">Type Conversion and Default Values</a></p>
</li>
<li><p><a class="post-section-overview" href="#heading-how-to-create-a-simple-config-manager">How to Create a Simple Config Manager</a></p>
</li>
<li><p><a class="post-section-overview" href="#heading-how-to-work-with-multiple-sections-in-ini-files">How to Work with Multiple Sections in INI Files</a></p>
</li>
<li><p><a class="post-section-overview" href="#heading-how-to-write-configuration-files">How to Write Configuration Files</a></p>
</li>
</ol>
<h2 id="heading-understanding-the-ini-file-format">Understanding the INI File Format</h2>
<p>INI files organize configuration into sections, where each section contains key-value pairs. This structure is useful for applications with multiple components or environments. Let's look at what an INI file looks like before we parse it.</p>
<p>Create a file named <code>app.ini</code>:</p>
<pre class="language-plaintext" tabindex="0"><code class="language-plaintext">[database]
host = localhost
port = 5432
username = app_user
password = secure_password
pool_size = 10
ssl_enabled = true

[server]
host = 0.0.0.0
port = 8000
debug = false

[logging]
level = INFO
file = app.log
</code></pre>
<p>This file contains three sections: database, server, and logging. Each section groups related settings together, making the configuration easy to understand and maintain.</p>
<h2 id="heading-basic-configparser-usage">Basic ConfigParser Usage</h2>
<p>The <code>configparser</code> module provides the <code>ConfigParser</code> class, which handles all the parsing work. Here's how to read and access configuration values:</p>
<pre class="language-python" tabindex="0"><code class="language-python"><span class="token keyword">import</span> configparser

config <span class="token operator">=</span> configparser<span class="token punctuation">.</span>ConfigParser<span class="token punctuation">(</span><span class="token punctuation">)</span>
config<span class="token punctuation">.</span>read<span class="token punctuation">(</span><span class="token string">'app.ini'</span><span class="token punctuation">)</span>

<span class="token comment"># Access values from sections</span>
db_host <span class="token operator">=</span> config<span class="token punctuation">[</span><span class="token string">'database'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'host'</span><span class="token punctuation">]</span>
db_port <span class="token operator">=</span> config<span class="token punctuation">[</span><span class="token string">'database'</span><span class="token punctuation">]</span><span class="token punctuation">[</span><span class="token string">'port'</span><span class="token punctuation">]</span>

<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Database: </span><span class="token interpolation"><span class="token punctuation">{</span>db_host<span class="token punctuation">}</span></span><span class="token string">:</span><span class="token interpolation"><span class="token punctuation">{</span>db_port<span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>
<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Sections: </span><span class="token interpolation"><span class="token punctuation">{</span>config<span class="token punctuation">.</span>sections<span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>
</code></pre>
<p>This code shows the basic workflow:</p>
<ul>
<li><p>create a <code>ConfigParser</code> object,</p>
</li>
<li><p>read your INI file,</p>
</li>
<li><p>then access values using dictionary-like syntax.</p>
</li>
</ul>
<p>The first bracket contains the section name, and the second contains the key.</p>
<p>Create the <code>app.ini</code> file and run the above code. You should see the following output:</p>
<pre class="language-plaintext" tabindex="0"><code class="language-plaintext">Database: localhost:5432
Sections: ['database', 'server', 'logging']
</code></pre>
<h2 id="heading-type-conversion-and-default-values">Type Conversion and Default Values</h2>
<p>Configuration values in INI files are stored as strings, but you often need them as integers, booleans, or floats. <code>ConfigParser</code> provides convenient methods for type conversion as shown here:</p>
<pre class="language-python" tabindex="0"><code class="language-python"><span class="token keyword">import</span> configparser

config <span class="token operator">=</span> configparser<span class="token punctuation">.</span>ConfigParser<span class="token punctuation">(</span><span class="token punctuation">)</span>
config<span class="token punctuation">.</span>read<span class="token punctuation">(</span><span class="token string">'app.ini'</span><span class="token punctuation">)</span>

<span class="token comment"># Automatic type conversion</span>
db_port <span class="token operator">=</span> config<span class="token punctuation">.</span>getint<span class="token punctuation">(</span><span class="token string">'database'</span><span class="token punctuation">,</span> <span class="token string">'port'</span><span class="token punctuation">)</span>
ssl_enabled <span class="token operator">=</span> config<span class="token punctuation">.</span>getboolean<span class="token punctuation">(</span><span class="token string">'database'</span><span class="token punctuation">,</span> <span class="token string">'ssl_enabled'</span><span class="token punctuation">)</span>

<span class="token comment"># With fallback defaults</span>
max_retries <span class="token operator">=</span> config<span class="token punctuation">.</span>getint<span class="token punctuation">(</span><span class="token string">'database'</span><span class="token punctuation">,</span> <span class="token string">'max_retries'</span><span class="token punctuation">,</span> fallback<span class="token operator">=</span><span class="token number">3</span><span class="token punctuation">)</span>
timeout <span class="token operator">=</span> config<span class="token punctuation">.</span>getfloat<span class="token punctuation">(</span><span class="token string">'database'</span><span class="token punctuation">,</span> <span class="token string">'timeout'</span><span class="token punctuation">,</span> fallback<span class="token operator">=</span><span class="token number">30.0</span><span class="token punctuation">)</span>

<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Port: </span><span class="token interpolation"><span class="token punctuation">{</span>db_port<span class="token punctuation">}</span></span><span class="token string">, SSL: </span><span class="token interpolation"><span class="token punctuation">{</span>ssl_enabled<span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>
</code></pre>
<p>In this code, the <code>getint()</code>, <code>getboolean()</code>, and <code>getfloat()</code> methods convert string values to the appropriate type. The <code>fallback</code> parameter provides a default value when the key doesn't exist, preventing errors.</p>
<p>When you run the above code, you’ll get:</p>
<pre class="language-plaintext" tabindex="0"><code class="language-plaintext">Port: 5432, SSL: True
</code></pre>
<h2 id="heading-how-to-create-a-simple-config-manager">How to Create a Simple Config Manager</h2>
<p>A practical approach is to wrap <code>ConfigParser</code> in a class that validates configuration and provides easy access to settings:</p>
<pre class="language-python" tabindex="0"><code class="language-python"><span class="token keyword">import</span> configparser
<span class="token keyword">from</span> pathlib <span class="token keyword">import</span> Path

<span class="token keyword">class</span> <span class="token class-name">ConfigManager</span><span class="token punctuation">:</span>
    <span class="token keyword">def</span> <span class="token function">__init__</span><span class="token punctuation">(</span>self<span class="token punctuation">,</span> config_file<span class="token operator">=</span><span class="token string">'app.ini'</span><span class="token punctuation">)</span><span class="token punctuation">:</span>
        self<span class="token punctuation">.</span>config <span class="token operator">=</span> configparser<span class="token punctuation">.</span>ConfigParser<span class="token punctuation">(</span><span class="token punctuation">)</span>

        <span class="token keyword">if</span> <span class="token keyword">not</span> Path<span class="token punctuation">(</span>config_file<span class="token punctuation">)</span><span class="token punctuation">.</span>exists<span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">:</span>
            <span class="token keyword">raise</span> FileNotFoundError<span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Config file not found: </span><span class="token interpolation"><span class="token punctuation">{</span>config_file<span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>

        self<span class="token punctuation">.</span>config<span class="token punctuation">.</span>read<span class="token punctuation">(</span>config_file<span class="token punctuation">)</span>

    <span class="token keyword">def</span> <span class="token function">get_database_config</span><span class="token punctuation">(</span>self<span class="token punctuation">)</span><span class="token punctuation">:</span>
        db <span class="token operator">=</span> self<span class="token punctuation">.</span>config<span class="token punctuation">[</span><span class="token string">'database'</span><span class="token punctuation">]</span>
        <span class="token keyword">return</span> <span class="token punctuation">{</span>
            <span class="token string">'host'</span><span class="token punctuation">:</span> db<span class="token punctuation">.</span>get<span class="token punctuation">(</span><span class="token string">'host'</span><span class="token punctuation">)</span><span class="token punctuation">,</span>
            <span class="token string">'port'</span><span class="token punctuation">:</span> db<span class="token punctuation">.</span>getint<span class="token punctuation">(</span><span class="token string">'port'</span><span class="token punctuation">)</span><span class="token punctuation">,</span>
            <span class="token string">'username'</span><span class="token punctuation">:</span> db<span class="token punctuation">.</span>get<span class="token punctuation">(</span><span class="token string">'username'</span><span class="token punctuation">)</span><span class="token punctuation">,</span>
            <span class="token string">'password'</span><span class="token punctuation">:</span> db<span class="token punctuation">.</span>get<span class="token punctuation">(</span><span class="token string">'password'</span><span class="token punctuation">)</span><span class="token punctuation">,</span>
            <span class="token string">'pool_size'</span><span class="token punctuation">:</span> db<span class="token punctuation">.</span>getint<span class="token punctuation">(</span><span class="token string">'pool_size'</span><span class="token punctuation">,</span> fallback<span class="token operator">=</span><span class="token number">5</span><span class="token punctuation">)</span>
        <span class="token punctuation">}</span>
</code></pre>
<p>This manager class validates that the file exists and provides clean methods to access configuration. It returns dictionaries with properly typed values.</p>
<p>And you can use it like so:</p>
<pre class="language-python" tabindex="0"><code class="language-python">config <span class="token operator">=</span> ConfigManager<span class="token punctuation">(</span><span class="token string">'app.ini'</span><span class="token punctuation">)</span>
db_config <span class="token operator">=</span> config<span class="token punctuation">.</span>get_database_config<span class="token punctuation">(</span><span class="token punctuation">)</span>
<span class="token keyword">print</span><span class="token punctuation">(</span>db_config<span class="token punctuation">)</span>
</code></pre>
<p>This outputs:</p>
<pre class="language-plaintext" tabindex="0"><code class="language-plaintext">{'host': 'localhost', 'port': 5432, 'username': 'app_user', 'password': 'secure_password', 'pool_size': 10}
</code></pre>
<h2 id="heading-how-to-work-with-multiple-sections-in-ini-files">How to Work with Multiple Sections in INI Files</h2>
<p>You can organize different parts of your application into separate sections and access them independently:</p>
<pre class="language-python" tabindex="0"><code class="language-python"><span class="token keyword">import</span> configparser

config <span class="token operator">=</span> configparser<span class="token punctuation">.</span>ConfigParser<span class="token punctuation">(</span><span class="token punctuation">)</span>
config<span class="token punctuation">.</span>read<span class="token punctuation">(</span><span class="token string">'app.ini'</span><span class="token punctuation">)</span>

<span class="token comment"># Get all options in a section as a dictionary</span>
db_settings <span class="token operator">=</span> <span class="token builtin">dict</span><span class="token punctuation">(</span>config<span class="token punctuation">[</span><span class="token string">'database'</span><span class="token punctuation">]</span><span class="token punctuation">)</span>
server_settings <span class="token operator">=</span> <span class="token builtin">dict</span><span class="token punctuation">(</span>config<span class="token punctuation">[</span><span class="token string">'server'</span><span class="token punctuation">]</span><span class="token punctuation">)</span>

<span class="token comment"># Check if a section exists</span>
<span class="token keyword">if</span> config<span class="token punctuation">.</span>has_section<span class="token punctuation">(</span><span class="token string">'cache'</span><span class="token punctuation">)</span><span class="token punctuation">:</span>
    cache_enabled <span class="token operator">=</span> config<span class="token punctuation">.</span>getboolean<span class="token punctuation">(</span><span class="token string">'cache'</span><span class="token punctuation">,</span> <span class="token string">'enabled'</span><span class="token punctuation">)</span>
<span class="token keyword">else</span><span class="token punctuation">:</span>
    cache_enabled <span class="token operator">=</span> <span class="token boolean">False</span>

<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Database settings: </span><span class="token interpolation"><span class="token punctuation">{</span>db_settings<span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>
<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string-interpolation"><span class="token string">f"Caching enabled: </span><span class="token interpolation"><span class="token punctuation">{</span>cache_enabled<span class="token punctuation">}</span></span><span class="token string">"</span></span><span class="token punctuation">)</span>
</code></pre>
<p>The <code>dict()</code> conversion gives you all key-value pairs from a section at once. The <code>has_section()</code> method lets you conditionally handle optional configuration sections.</p>
<p>Running the above code should give you the following output:</p>
<pre class="language-plaintext" tabindex="0"><code class="language-plaintext">Database settings: {'host': 'localhost', 'port': '5432', 'username': 'app_user', 'password': 'secure_password', 'pool_size': '10', 'ssl_enabled': 'true'}
Caching enabled: False
</code></pre>
<h2 id="heading-how-to-write-configuration-files">How to Write Configuration Files</h2>
<p><code>ConfigParser</code> can also create and modify INI files, which is useful for saving user preferences or generating config templates:</p>
<pre class="language-python" tabindex="0"><code class="language-python"><span class="token keyword">import</span> configparser

config <span class="token operator">=</span> configparser<span class="token punctuation">.</span>ConfigParser<span class="token punctuation">(</span><span class="token punctuation">)</span>

<span class="token comment"># Add sections and values</span>
config<span class="token punctuation">[</span><span class="token string">'database'</span><span class="token punctuation">]</span> <span class="token operator">=</span> <span class="token punctuation">{</span>
    <span class="token string">'host'</span><span class="token punctuation">:</span> <span class="token string">'localhost'</span><span class="token punctuation">,</span>
    <span class="token string">'port'</span><span class="token punctuation">:</span> <span class="token string">'5432'</span><span class="token punctuation">,</span>
    <span class="token string">'username'</span><span class="token punctuation">:</span> <span class="token string">'myapp'</span>
<span class="token punctuation">}</span>

config<span class="token punctuation">[</span><span class="token string">'server'</span><span class="token punctuation">]</span> <span class="token operator">=</span> <span class="token punctuation">{</span>
    <span class="token string">'host'</span><span class="token punctuation">:</span> <span class="token string">'0.0.0.0'</span><span class="token punctuation">,</span>
    <span class="token string">'port'</span><span class="token punctuation">:</span> <span class="token string">'8000'</span><span class="token punctuation">,</span>
    <span class="token string">'debug'</span><span class="token punctuation">:</span> <span class="token string">'false'</span>
<span class="token punctuation">}</span>

<span class="token comment"># Write to file</span>
<span class="token keyword">with</span> <span class="token builtin">open</span><span class="token punctuation">(</span><span class="token string">'generated.ini'</span><span class="token punctuation">,</span> <span class="token string">'w'</span><span class="token punctuation">)</span> <span class="token keyword">as</span> configfile<span class="token punctuation">:</span>
    config<span class="token punctuation">.</span>write<span class="token punctuation">(</span>configfile<span class="token punctuation">)</span>

<span class="token keyword">print</span><span class="token punctuation">(</span><span class="token string">"Configuration file created!"</span><span class="token punctuation">)</span>
</code></pre>
<p>This code creates a new INI file from scratch. The write() method saves the configuration in the proper INI format with sections and key-value pairs.</p>
<h2 id="heading-conclusion">Conclusion</h2>
<p>When environment variables aren't enough and you need grouped settings for different components, INI files are your answer.</p>
<p>The format is human-readable, <code>ConfigParser</code> handles type conversion automatically, and it's built into Python's standard library. Wrap it in a configuration class for validation and clean access patterns.</p>
<p>Also remember:</p>
<ul>
<li><p>Organize by component. Use sections to group related settings.</p>
</li>
<li><p>Use type conversion methods. Always use <code>getint()</code>, <code>getboolean()</code>, and <code>getfloat()</code> rather than manual conversion. They handle edge cases better.</p>
</li>
<li><p>Provide sensible defaults. Use the <code>fallback</code> parameter for optional settings so your application works with minimal configuration.</p>
</li>
<li><p>Validate early. Check that required sections and keys exist at startup before attempting to use them.</p>
</li>
<li><p>Keep secrets separate. Don't commit INI files with passwords to version control. Use <code>.ini.example</code> files with dummy values as templates.</p>
</li>
</ul>
<p>In the next article, you’ll learn how to work with TOML files in Python. Until then, keep coding!</p>


                        </section>
                        
                            <div class="sidebar">
                                
                                    
                                    <script>var localizedAdText = "ADVERTISEMENT";</script>
                                
                            <div class="ad-wrapper"><div class="ad-text" style="visibility: inherit;">ADVERTISEMENT</div><div id="side-gam-ad-0" class="side-bar-ad-slot" data-google-query-id="CPPHzIHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_0__container__" style="border: 0pt none;"><iframe id="google_ads_iframe_/23075930536/post-side_0" name="google_ads_iframe_/23075930536/post-side_0" title="3rd party ad content" width="160" height="600" scrolling="no" marginwidth="0" marginheight="0" frameborder="0" aria-label="Advertisement" tabindex="0" allow="private-state-token-redemption;attribution-reporting" data-load-complete="true" style="border: 0px; vertical-align: bottom;" data-google-container-id="1"></iframe></div></div></div><div class="ad-wrapper"><div class="ad-text" style="visibility: inherit;">ADVERTISEMENT</div><div id="side-gam-ad-1" class="side-bar-ad-slot" data-google-query-id="CPTHzIHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_1__container__" style="border: 0pt none; display: inline-block; width: 300px; height: 600px;"><iframe frameborder="0" src="https://a71dd77bd358dde1367ad13618b898fa.safeframe.googlesyndication.com/safeframe/1-0-45/html/container.html" id="google_ads_iframe_/23075930536/post-side_1" title="3rd party ad content" name="" scrolling="no" marginwidth="0" marginheight="0" width="300" height="600" data-is-safeframe="true" sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-top-navigation-by-user-activation" allow="private-state-token-redemption;attribution-reporting" aria-label="Advertisement" tabindex="0" data-google-container-id="2" style="border: 0px; vertical-align: bottom;" data-load-complete="true"></iframe></div></div></div><div class="ad-wrapper"><div class="ad-text" style="visibility: inherit;">ADVERTISEMENT</div><div id="side-gam-ad-2" class="side-bar-ad-slot" data-google-query-id="CPXHzIHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_2__container__" style="border: 0pt none; display: inline-block; width: 300px; height: 250px;"><iframe frameborder="0" src="https://a71dd77bd358dde1367ad13618b898fa.safeframe.googlesyndication.com/safeframe/1-0-45/html/container.html" id="google_ads_iframe_/23075930536/post-side_2" title="3rd party ad content" name="" scrolling="no" marginwidth="0" marginheight="0" width="300" height="250" data-is-safeframe="true" sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-top-navigation-by-user-activation" allow="private-state-token-redemption;attribution-reporting" aria-label="Advertisement" tabindex="0" data-google-container-id="3" style="border: 0px; vertical-align: bottom;" data-load-complete="true"></iframe></div></div></div><div class="ad-wrapper"><div class="ad-text" style="visibility: inherit;">ADVERTISEMENT</div><div id="side-gam-ad-3" class="side-bar-ad-slot" data-google-query-id="CPfHzIHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_3__container__" style="border: 0pt none;"><iframe id="google_ads_iframe_/23075930536/post-side_3" name="google_ads_iframe_/23075930536/post-side_3" title="3rd party ad content" width="300" height="600" scrolling="no" marginwidth="0" marginheight="0" frameborder="0" aria-label="Advertisement" tabindex="0" allow="private-state-token-redemption;attribution-reporting" data-load-complete="true" style="border: 0px; vertical-align: bottom;" data-google-container-id="4"></iframe></div></div></div><div class="ad-wrapper"><div class="ad-text" style="visibility: inherit;">ADVERTISEMENT</div><div id="side-gam-ad-4" class="side-bar-ad-slot" data-google-query-id="CPjHzIHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_4__container__" style="border: 0pt none; display: inline-block; width: 300px; height: 600px;"><iframe frameborder="0" src="https://a71dd77bd358dde1367ad13618b898fa.safeframe.googlesyndication.com/safeframe/1-0-45/html/container.html" id="google_ads_iframe_/23075930536/post-side_4" title="3rd party ad content" name="" scrolling="no" marginwidth="0" marginheight="0" width="300" height="600" data-is-safeframe="true" sandbox="allow-forms allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-top-navigation-by-user-activation" allow="private-state-token-redemption;attribution-reporting" aria-label="Advertisement" tabindex="0" data-google-container-id="5" style="border: 0px; vertical-align: bottom;" data-load-complete="true"></iframe></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-5" class="side-bar-ad-slot" data-google-query-id="COioyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_5__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-6" class="side-bar-ad-slot" data-google-query-id="COmoyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_6__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-7" class="side-bar-ad-slot" data-google-query-id="COqoyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_7__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-8" class="side-bar-ad-slot" data-google-query-id="COuoyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_8__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-9" class="side-bar-ad-slot" data-google-query-id="COyoyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_9__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-10" class="side-bar-ad-slot" data-google-query-id="CO2oyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_10__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-11" class="side-bar-ad-slot" data-google-query-id="CO6oyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_11__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div><div class="ad-wrapper"><div class="ad-text">ADVERTISEMENT</div><div id="side-gam-ad-12" class="side-bar-ad-slot" data-google-query-id="CO-oyoHHrpADFbq90QQdMgEoig"><div id="google_ads_iframe_/23075930536/post-side_12__container__" style="border: 0pt none; width: 292px; height: 0px;"></div></div></div></div>
                        
                    </div>
                    <hr>
                    
                        <div class="post-full-author-header" data-test-label="author-header-with-bio">
                            
                                
    
    
    

    <section class="author-card" data-test-label="author-card">
        
            
    <img srcset="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg 60w" sizes="60px" src="https://cdn.hashnode.com/res/hashnode/image/upload/v1640182085352/em-AboBL8.jpeg" class="author-profile-image" alt="Bala Priya C" width="1646" height="1460" onerror="this.style.display='none'" loading="lazy" data-test-label="profile-image">
  
        

        <section class="author-card-content ">
            <span class="author-card-name">
                <a href="/news/author/balapriyac/" data-test-label="profile-link">
                    
                        Bala Priya C
                    
                </a>
            </span>
            
                
                    <p data-test-label="author-bio">I'm a self-taught programmer and a technical writer from India. I enjoy reading, writing, and coding. I share my learning with the developer community by writing beginner-friendly programming tutorials.
</p>
                
            
        </section>
    </section>

                            
                        </div>
                        <hr>
                    

                    
                    
                        
    


<p data-test-label="social-row-cta" class="social-row">
    If this article was helpful, <button id="tweet-btn" class="cta-button" data-test-label="tweet-button" onclick="window.open(
    'https://x.com/intent/post?text=How%20to%20Parse%20INI%20Config%20Files%20in%20Python%20with%20Configparser%0A%0Ahttps://www.freecodecamp.org/news/how-to-parse-ini-config-files-in-python-with-configparser/',
    'share-twitter',
    'width=550, height=235'
  ); return false;">share it</button>.
</p>


    
    <script>document.addEventListener("DOMContentLoaded",()=>{const t=document.getElementById("tweet-btn"),n=window.location,e="How%20to%20Parse%20INI%20Config%20Files%20in%20Python%20with%20Configparser".replace(/&#39;/g,"%27"),o="",i="",r=Boolean("");let s;if(r&&(o||i)){const t={originalPostAuthor:"",currentPostAuthor:"Bala Priya C"};s=encodeURIComponent(`Thank you ${o||t.originalPostAuthor} for writing this helpful article, and ${i||t.currentPostAuthor} for translating it.`)}else!r&&i&&(s=encodeURIComponent(`Thank you ${i} for writing this helpful article.`));const a=`window.open(\n    '${s?`https://x.com/intent/post?text=${s}%0A%0A${e}%0A%0A${n}`:`https://x.com/intent/post?text=${e}%0A%0A${n}`}',\n    'share-twitter',\n    'width=550, height=235'\n  ); return false;`;t.setAttribute("onclick",a)});</script>


                        

<div class="learn-cta-row" data-test-label="learn-cta-row">
    <p>
        Learn to code for free. freeCodeCamp's open source curriculum has helped more than 40,000 people get jobs as developers. <a href="https://www.freecodecamp.org/learn/" class="cta-button" id="learn-to-code-cta" rel="noopener noreferrer" target="_blank">Get started</a>
    </p>
</div>

                    
                </section>
                
                    <div class="banner-ad-bottom">
                        
                            

<div class="ad-text" data-test-label="ad-text">ADVERTISEMENT</div>
<div style="height: auto;" id="gam-ad-bottom">
<div id="google_ads_iframe_/23075930536/post-bottom_0__container__" style="border: 0pt none; display: inline-block;"></div></div>

                        
                    </div>
                
            </article>

```