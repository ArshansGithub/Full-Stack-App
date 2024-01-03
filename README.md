# Full-Stack-App
Frontend built-in vanilla HTML, CSS, and JS using a Python Flask backend with MongoDB and authentication.

I created an automated program to get myself Chipotle promo codes. I wanted to challenge myself so I created this full-stack application to access my promo codes on the go in a secure but easy-to-use way. This project was great to learn, and I feel better prepared to tackle further full stack-requiring problems I may face down the road.

A quick explanation of the features within this project.
- Authentication including IP check (each account has a whitelisted list of IP addresses which can be dynamically added and removed from), too many failed attempts causes timeout which increases with further failed attempts, account must be manually verified, and normal user/password requirement
- IP Check configurable via a discord bot that connects to the same database. Using slash commands you can add, remove, and view ip addresses from the whitelist of a desired account
- Self designed and developed UI with vanilla HTML, CSS, and JS
- Robust set of features for interacting with coupon codes (Mass copy, singular copy, filter, etc)
- Pagination for dynamic resizing of elements + Mobile Friendly
