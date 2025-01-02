---
title: Team
nav:
  order: 3
  tooltip: About our team
---

# {% include icon.html icon="fa-solid fa-users" %}Team

Our team consists of talented multidisciplinary researchers across cardiovascular disease/heart failure, artificial intelligence, and data science. 

{% include section.html %}


<h2 style="text-align: center;">Core Team</h2>

{% include list.html data="members" component="portrait" filters="role: pi, group: " %}
{% include list.html data="members" component="portrait" filters="role: le, group: " %}

{% include section.html %}

<h2 style="text-align: center;">Collaborating Investigators</h2>

{% include list.html data="members" component="portrait" filters="role: espo, group: " %}
{% include list.html data="members" component="portrait" filters="group: co-i" %}
<!-- {% include list.html data="members" component="portrait" filters="role: ^(?!pi$), group: " %} -->

{% include section.html %}

<h2 style="text-align: center;">Medical Students, Residents, and Fellows</h2>

{% include list.html data="members" component="portrait" filters="role: fellow, group: " %}
{% include list.html data="members" component="portrait" filters="role: resident, group: " %}
{% include list.html data="members" component="portrait" filters="role: medstudent, group: " %}

