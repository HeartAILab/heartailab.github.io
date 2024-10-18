---
title: Team
nav:
  order: 3
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Team

Our team consists of talented multidisciplinary researchers across cardiovascular disease/heart failure, artificial intelligence, and data science. 

{% include section.html %}

{% include list.html data="members" component="portrait" filters="role: pi, group: " %}
{% include list.html data="members" component="portrait" filters="role: ^(?!pi$), group: " %}

{% include section.html background="images/background.jpg" dark=true %}

We are growing and we are always looking for talented, motivated, and driven students, residents, fellows, and post-docs to innovate with us. Feel free to reach out if you are interested in joining!


## Alumni
{% include section.html %}

{% include list.html data="members" component="portrait" filters="role: pi, group: alumni" %}
{% include list.html data="members" component="portrait" filters="role: ^(?!pi$), group: alumni" %}
