# To extract the information we need from the realpython.com articles , we need to follow this steps: 
### 1. Get the link of the article : 
In the homepage of realpython.com, we can find the links of the articles in the div class "card border-0", specifically in the anchor tag <a> inside it. 

### 2. Get the article title:
In the homepage of realpython.com, the article title is located inside the h2 tag with class "card-title h4 my-0 py-0", which is inside the anchor tag <a>.

This is an example of the html structure of the article card where we can find the title and link:
```html
<div class="card border-0">
  <a href="/polars-vs-pandas/">
    <div class="embed-responsive embed-responsive-16by9">
      
        <img loading="lazy" class="card-img-top m-0 p-0 embed-responsive-item rounded" style="object-fit: contain; background: #ffc873;" alt="Polars vs pandas: What's the Difference?" src="https://files.realpython.com/media/Polars-vs-Pandas_Watermarked.0021a1a79975.jpg" width="1920" height="1080" srcset="/cdn-cgi/image/width=480,format=auto/https://files.realpython.com/media/Polars-vs-Pandas_Watermarked.0021a1a79975.jpg 480w, /cdn-cgi/image/width=640,format=auto/https://files.realpython.com/media/Polars-vs-Pandas_Watermarked.0021a1a79975.jpg 640w, /cdn-cgi/image/width=960,format=auto/https://files.realpython.com/media/Polars-vs-Pandas_Watermarked.0021a1a79975.jpg 960w, /cdn-cgi/image/width=1920,format=auto/https://files.realpython.com/media/Polars-vs-Pandas_Watermarked.0021a1a79975.jpg 1920w" sizes="(min-width: 1200px) 330px, (min-width: 1000px) 290px, (min-width: 780px) 330px, (min-width: 580px) 510px, calc(100vw - 30px)">
      
      
    </div>
  </a>
  <div class="card-body m-0 p-0 mt-2">
    <a class=" " href="/polars-vs-pandas/">
      <h2 class="card-title h4 my-0 py-0">Polars vs pandas: What's the Difference?</h2>
    </a>
    <p class="card-text text-muted text-truncate small">
      
        <span class="mr-2">Oct 15, 2025</span>
      
      
      
        <span class="icon baseline" aria-hidden="true"><svg aria-hidden="true"><use href="/static/icons.0fae35ff985f.svg#@category"></use></svg></span>
        
          
<a href="/tutorials/intermediate/" class="badge badge-light text-muted" data-previewable="">intermediate</a>

        
          
<a href="/tutorials/data-science/" class="badge badge-light text-muted" data-previewable="">data-science</a>

        
          
<a href="/tutorials/python/" class="badge badge-light text-muted" data-previewable="">python</a>

        
      
    </p>
  </div>
</div>
```


<div class="card mt-3" id="author">
  <p class="card-header h3">About <strong>Ian Eyre</strong></p>
```

### 3. Get the author name:
The author name is located in the article page , once we extract the link of the article, we can navigate to it and find the author name in the div class "card mt-3" with id "author", specifically in the strong tag inside a p tag with class "card-header h3".

This is an example of the html structure of the auhtor page where we can find the author name:
``` html

<div class="card mt-3" id="author">
  <p class="card-header h3">About <strong>Ian Eyre</strong></p>
  <div class="card-body">
    <div class="container p-0">
      <div class="row">
        <div class="col-12 col-md-3 align-self-center">
          <a href="/team/ieyre/" aria-hidden="true" tabindex="-1">
            <img loading="lazy" src="/cdn-cgi/image/width=644,height=644,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png" srcset="/cdn-cgi/image/width=161,height=161,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 161w, /cdn-cgi/image/width=214,height=214,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 214w, /cdn-cgi/image/width=322,height=322,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 322w, /cdn-cgi/image/width=644,height=644,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 644w" sizes="(min-width: 580px) 154px, calc(33.08vw - 24px)" width="644" height="644" style="background: #a6b96f;" class="d-block d-md-none rounded-circle img-fluid w-33 mb-0 mx-auto" alt="Ian Eyre">
            <img loading="lazy" src="/cdn-cgi/image/width=644,height=644,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png" srcset="/cdn-cgi/image/width=161,height=161,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 161w, /cdn-cgi/image/width=214,height=214,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 214w, /cdn-cgi/image/width=322,height=322,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 322w, /cdn-cgi/image/width=644,height=644,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Me_at_Graceland.f88418f34d62.fa6f5ab743da.png 644w" sizes="(min-width: 1200px) 140px, calc(-1.5vw + 137px)" width="644" height="644" style="background: #a6b96f;" class="d-none d-md-block rounded-circle img-fluid w-100 mb-0" alt="Ian Eyre">
          </a>
        </div>
        <div class="col mt-3">
          <p>Ian is an avid Pythonista and Real Python contributor who loves to learn and teach others.</p>
          <a href="/team/ieyre/" class="card-link">» More about Ian</a>
        </div>
      </div>
    </div>
  </div>
  
  <hr class="my-0">
  <div class="card-body pb-0">
    <div class="container">
      <div class="row">
        <p><em>Each tutorial at Real Python is created by a team of developers so that it meets our high quality standards. The team members who worked on this tutorial are:</em></p>
      </div>

      
        
          <div class="row align-items-center w-100 mx-auto">
        

        <div class="col-4 col-sm-2 align-self-center">
          
            <a href="/team/asantos/" aria-hidden="true" tabindex="-1" data-previewable=""><img loading="lazy" src="/cdn-cgi/image/width=500,height=500,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Aldren_Santos_Real_Python.6b0861d8b841.png" srcset="/cdn-cgi/image/width=125,height=125,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Aldren_Santos_Real_Python.6b0861d8b841.png 125w, /cdn-cgi/image/width=166,height=166,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Aldren_Santos_Real_Python.6b0861d8b841.png 166w, /cdn-cgi/image/width=250,height=250,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Aldren_Santos_Real_Python.6b0861d8b841.png 250w, /cdn-cgi/image/width=500,height=500,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Aldren_Santos_Real_Python.6b0861d8b841.png 500w" sizes="(min-width: 1200px) 73px, (min-width: 780px) calc(-0.75vw + 69px), (min-width: 580px) 43px, calc(33.46vw - 64px)" width="500" height="500" style="background: #d2cec3;" class="rounded-circle img-fluid w-100" alt="Aldren Santos"></a>
          
        </div>
        <div class="col pl-0 d-none d-sm-block">
          <a href="/team/asantos/" class="card-link small" data-previewable=""><p>Aldren</p></a>
        </div>

        

        
      
        

        <div class="col-4 col-sm-2 align-self-center">
          
            <a href="/team/bweleschuk/" aria-hidden="true" tabindex="-1" data-previewable=""><img loading="lazy" src="/cdn-cgi/image/width=320,height=320,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/IMG_3324_1.50b309355fc1.jpg" srcset="/cdn-cgi/image/width=80,height=80,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/IMG_3324_1.50b309355fc1.jpg 80w, /cdn-cgi/image/width=106,height=106,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/IMG_3324_1.50b309355fc1.jpg 106w, /cdn-cgi/image/width=160,height=160,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/IMG_3324_1.50b309355fc1.jpg 160w, /cdn-cgi/image/width=320,height=320,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/IMG_3324_1.50b309355fc1.jpg 320w" sizes="(min-width: 1200px) 73px, (min-width: 780px) calc(-0.75vw + 69px), (min-width: 580px) 43px, calc(33.46vw - 64px)" width="320" height="320" style="background: #d6d4ad;" class="rounded-circle img-fluid w-100" alt="Brenda Weleschuk"></a>
          
        </div>
        <div class="col pl-0 d-none d-sm-block">
          <a href="/team/bweleschuk/" class="card-link small" data-previewable=""><p>Brenda</p></a>
        </div>

        

        
      
        

        <div class="col-4 col-sm-2 align-self-center">
          
            <a href="/team/bzaczynski/" aria-hidden="true" tabindex="-1" data-previewable=""><img loading="lazy" src="/cdn-cgi/image/width=1694,height=1694,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/coders_lab_2109368.259b1599fbee.jpg" srcset="/cdn-cgi/image/width=423,height=423,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/coders_lab_2109368.259b1599fbee.jpg 423w, /cdn-cgi/image/width=564,height=564,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/coders_lab_2109368.259b1599fbee.jpg 564w, /cdn-cgi/image/width=847,height=847,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/coders_lab_2109368.259b1599fbee.jpg 847w, /cdn-cgi/image/width=1694,height=1694,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/coders_lab_2109368.259b1599fbee.jpg 1694w" sizes="(min-width: 1200px) 73px, (min-width: 780px) calc(-0.75vw + 69px), (min-width: 580px) 43px, calc(33.46vw - 64px)" width="1694" height="1694" style="background: #dadada;" class="rounded-circle img-fluid w-100" alt="Bartosz Zaczyński"></a>
          
        </div>
        <div class="col pl-0 d-none d-sm-block">
          <a href="/team/bzaczynski/" class="card-link small" data-previewable=""><p>Bartosz</p></a>
        </div>

        

        
          </div>
        
      
        
          <div class="row align-items-center w-100 mx-auto">
        

        <div class="col-4 col-sm-2 align-self-center">
          
            <a href="/team/sgruppetta/" aria-hidden="true" tabindex="-1" data-previewable=""><img loading="lazy" src="/cdn-cgi/image/width=400,height=400,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Stephen_inside_2_BW_2_square_crop_2_low_res_2_copy.4a7e2d8bc19c.png" srcset="/cdn-cgi/image/width=100,height=100,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Stephen_inside_2_BW_2_square_crop_2_low_res_2_copy.4a7e2d8bc19c.png 100w, /cdn-cgi/image/width=133,height=133,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Stephen_inside_2_BW_2_square_crop_2_low_res_2_copy.4a7e2d8bc19c.png 133w, /cdn-cgi/image/width=200,height=200,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Stephen_inside_2_BW_2_square_crop_2_low_res_2_copy.4a7e2d8bc19c.png 200w, /cdn-cgi/image/width=400,height=400,fit=crop,gravity=auto,format=auto/https://files.realpython.com/media/Stephen_inside_2_BW_2_square_crop_2_low_res_2_copy.4a7e2d8bc19c.png 400w" sizes="(min-width: 1200px) 73px, (min-width: 780px) calc(-0.75vw + 69px), (min-width: 580px) 43px, calc(33.46vw - 64px)" width="400" height="400" style="background: #e7e7e7;" class="rounded-circle img-fluid w-100" alt="Stephen Gruppetta"></a>
          
        </div>
        <div class="col pl-0 d-none d-sm-block">
          <a href="/team/sgruppetta/" class="card-link small" data-previewable=""><p>Stephen</p></a>
        </div>

        
          
          
            <div class="col-4 col-sm-2 align-self-center"></div>
            <div class="col pl-0 d-none d-sm-block"></div>
            <div class="col-4 col-sm-2 align-self-center"></div>
            <div class="col pl-0 d-none d-sm-block"></div>
          
        

        
          </div>
        
      
    </div>
  </div>
  

</div>

```


