// Vercel function: receives the enquiry form and emails it through Resend.
// Environment variables (Vercel project settings):
//   RESEND_API_KEY  required
//   ENQUIRY_TO      optional, default info@mccgroup.in
//   ENQUIRY_FROM    optional, default "MCC Group Website <onboarding@resend.dev>"
//                   (use an address on a domain verified in Resend for production)
const THANKS = { en: '/thank-you/', hi: '/hi/thank-you/', mr: '/mr/thank-you/' };
const CONTACT = { en: '/contact/', hi: '/hi/contact/', mr: '/mr/contact/' };

function clean(v, max, multiline) {
  v = typeof v === 'string' ? v.trim() : '';
  v = multiline ? v.replace(/\r/g, '') : v.replace(/[\r\n]+/g, ' ');
  return v.slice(0, max);
}

module.exports = async (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const lang = Object.prototype.hasOwnProperty.call(THANKS, body.lang) ? body.lang : 'en';
  const go = (path) => { res.statusCode = 303; res.setHeader('Location', path); res.end(); };

  if (req.method !== 'POST') return go(CONTACT[lang]);
  if (body.website) return go(THANKS[lang]); // honeypot: pretend success

  const name = clean(body.name, 100);
  const phone = clean(body.phone, 20);
  const email = clean(body.email, 120);
  const type = clean(body.type, 100);
  const message = clean(body.message, 2000, true);
  const emailOk = email === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  if (!name || !phone || !message || !emailOk) return go(CONTACT[lang] + '?error=1');

  const key = process.env.RESEND_API_KEY;
  if (!key) return go(CONTACT[lang] + '?error=1');

  const payload = {
    from: process.env.ENQUIRY_FROM || 'MCC Group Website <onboarding@resend.dev>',
    to: [process.env.ENQUIRY_TO || 'info@mccgroup.in'],
    subject: 'Website enquiry: ' + name,
    text: `Name: ${name}\nPhone: ${phone}\nEmail: ${email || '-'}\nType of work: ${type}\nLanguage of page: ${lang}\n\n${message}\n`,
  };
  if (email) payload.reply_to = email;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return go(r.ok ? THANKS[lang] : CONTACT[lang] + '?error=1');
  } catch (e) {
    return go(CONTACT[lang] + '?error=1');
  }
};
