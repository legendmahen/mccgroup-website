# MCC Group website: review version

Upload the contents of the `dist` folder (index.html, assets/, hi/, mr/, etc.) to public_html on cPanel.
Pages use root-relative links, so the site must be served from the domain root (it will not work by double-clicking the files).

## Needs your confirmation before publishing
1. Which entity holds the Class 1A registration (site says "MCC Group is a Class 1A registered contractor with PWD Maharashtra").
2. Market complex: location stated as "Chimur, Maharashtra" (taken from the photo folder name). Official project name and client not shown.
3. Plant page lists only equipment type and make, from purchase/registration records (2006-2023). Not a confirmed current fleet. No registration numbers, owners or bank details are published.
4. Awards: only "award-winning projects in the region" is stated. Add names, bodies, years if you want them shown.
5. Hindi and Marathi texts need a native-speaker review (terms such as Executive Director, canal, dam, layout).
6. The four articles carry Mahendra Heda's name as author. He should read and approve them.
7. Careers copy is generic (no open roles; CV to info@mccgroup.in).
8. No director photos (per your instruction). No safety or quality statistics (none were provided).
9. Project case studies are not included yet; send details per photo set (location, client, scope, year).
10. Photos with people in them were left out. Two road photos had camera stamps cropped off.

## Technical
- enquiry.php sends enquiries to msh@mccgroup.in using the server's mail(); test it on the live host. If mail does not arrive, ask the host about SMTP.
- HTTPS redirect in .htaccess is commented out. Enable it once SSL works.
- robots.txt allows all crawlers; change if you want to block AI training bots.
- Sitemap, hreflang, JSON-LD (Organization, WebSite, Article, FAQPage, BreadcrumbList), llms.txt included.
- Rebuild: `python3 tools/build.py` (source in tools/).

## Vercel
- Deploy the `dist` folder. `vercel.json` maps /enquiry.php to the function in `dist/api/enquiry.js`.
- Add environment variable RESEND_API_KEY (from resend.com). Optional: ENQUIRY_TO, ENQUIRY_FROM.
- Until a domain is verified in Resend, mail can only go to the Resend account owner's email. Verify mccgroup.in in Resend, then set ENQUIRY_FROM to an address on it.
- On cPanel hosting, enquiry.php is used instead and /api/ is blocked by .htaccess.
