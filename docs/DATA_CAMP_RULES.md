## To extract the information from [datacamp.com/blog articles](https://www.datacamp.com/blog)
Follow the instructions bellow , do not use class names or id names as they are dynamic and can change frequently, use only the html structure and tags to locate the information needed.

### 1. Get the link of the article : 
In the datacamp blog page, each article has a data-trackid attribute with the format "media-card-/blog/article-slug" inside an anchor tag <a> that contains the link of the article.

### 2. Get the article title:
In the datacamp blog page, each article title is located inside an h2 that is in the anchor tag <a> that contains the link of the article.

### 3. Get the author name and article date:
in the article card locate a data-trackid attribute with the format "media-visit-author-profile" inside an anchor tag <a> that contains the link to the author's profile, the author name is located in a p tag .the article date is located in a p tag just before closing the main div of the article card.

This is an example of the html structure of the article card where we can find the article title, article link, article date, and author or authors names:
```html
<div data-trackid="media-card-How to Learn Python From Scratch in 2025: An Expert Guide" class="css-6sit9d"><div class="css-1yz7e9k"><object><a class="css-xlmvza" data-trackid="blog-category-badge" href="/blog/category/python" target="_self"><strong class="css-1isenrr">Python</strong></a></object><a class="css-yhqmm5" data-trackid="media-card-/blog/how-to-learn-python-expert-guide-1" href="/blog/how-to-learn-python-expert-guide" target="_self"><h2 class="css-1yr1rb9">How to Learn Python From Scratch in 2025: An Expert Guide</h2></a></div><div class="css-w7oivh"><div class="css-1p88eqm"><div class="hide-in-percy css-m5jzxa"><div class="hide-in-percy css-2r5hwm"><a class="css-xlmvza" data-trackid="media-visit-author-profile" href="/portfolio/mattcrabtree" target="_self"><img alt="Matt Crabtree's photo" loading="lazy" width="24" height="24" decoding="async" data-nimg="1" class="css-xah9so" style="color:transparent" srcset="https://media.datacamp.com/cms/matt_2.jpg?w=32 1x, https://media.datacamp.com/cms/matt_2.jpg?w=48 2x" src="https://media.datacamp.com/cms/matt_2.jpg?w=48"></a></div></div><div class="css-1ovs79h"><p class="css-198tbf7">Matt Crabtree<!-- --> </p></div></div><div class="css-1p88eqm"><div class="hide-in-percy css-m5jzxa"><div class="hide-in-percy css-2r5hwm"><a class="css-xlmvza" data-trackid="media-visit-author-profile" href="/portfolio/AAN94" target="_self"><img alt="Adel Nehme's photo" loading="lazy" width="24" height="24" decoding="async" data-nimg="1" class="css-xah9so" style="color:transparent" srcset="https://media.datacamp.com/cms/adel3.jpeg?w=32 1x, https://media.datacamp.com/cms/adel3.jpeg?w=48 2x" src="https://media.datacamp.com/cms/adel3.jpeg?w=48"></a></div></div><div class="css-1ovs79h"><p class="css-198tbf7">Adel Nehme<!-- --> </p></div></div><p class="css-xj3esj">November 22, 2024</p></div></div>
```

