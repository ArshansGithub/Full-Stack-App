# Full-Stack-App
Frontend built-in vanilla HTML, CSS, and JS using a Python Flask backend with MongoDB and authentication.

I created an automated program to get myself Chipotle promo codes. I wanted to challenge myself so I created this full-stack application to access my promo codes on the go in a secure but easy-to-use way. This project was great to learn, and I feel better prepared to tackle further full stack-requiring problems I may face down the road.

A quick explanation of the features within this project.
- Authentication including IP check (each account has a whitelisted list of IP addresses which can be dynamically added and removed from), too many failed attempts cause timeout which increases with further failed attempts, the account must be manually verified, and normal user/password requirement
- Account passwords are hashed using industry standards (bcrypt) and handling sessions via JWT tokens.
- IP Check configurable via a discord bot that connects to the same database. Using slash commands you can add, remove, and view IP addresses from the whitelist of a desired account
- Self-designed and developed UI with vanilla HTML, CSS, and JS
- Robust set of features for interacting with coupon codes (Mass copy, singular copy, filter, etc)
- Pagination for dynamic resizing of elements + Mobile Friendly
![Screenshot 2024-01-03 at 12-24-59 Home](https://github.com/ArshansGithub/Full-Stack-App/assets/111618520/2b87b4ef-c7ee-4435-8e8a-e7c0e1a6ef7f)
![Screenshot 2024-01-03 at 12-34-30 Home](https://github.com/ArshansGithub/Full-Stack-App/assets/111618520/d4ffebb7-525e-4985-aa59-6c31182725f1)
