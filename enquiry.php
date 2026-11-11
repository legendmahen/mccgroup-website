<?php
// Enquiry handler for mccgroup.in. Sends the enquiry to the sales mailbox and redirects to the thank-you page.
$to = 'msh@mccgroup.in';
$from = 'no-reply@mccgroup.in';
$thanks = ['en' => '/thank-you/', 'hi' => '/hi/thank-you/', 'mr' => '/mr/thank-you/'];
$contact = ['en' => '/contact/', 'hi' => '/hi/contact/', 'mr' => '/mr/contact/'];
$lang = isset($_POST['lang']) && isset($thanks[$_POST['lang']]) ? $_POST['lang'] : 'en';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: ' . $contact[$lang]); exit; }
if (!empty($_POST['website'])) { header('Location: ' . $thanks[$lang]); exit; } // honeypot: pretend success

function clean($v, $max, $multiline = false) {
    $v = isset($v) ? trim((string)$v) : '';
    $v = $multiline ? str_replace("\r", '', $v) : preg_replace('/[\r\n]+/', ' ', $v);
    return mb_substr($v, 0, $max);
}
$name = clean($_POST['name'] ?? '', 100);
$phone = clean($_POST['phone'] ?? '', 20);
$email = clean($_POST['email'] ?? '', 120);
$type = clean($_POST['type'] ?? '', 100);
$msg = clean($_POST['message'] ?? '', 2000, true);

$fail = $name === '' || $phone === '' || $msg === '' || ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL));
if ($fail) { header('Location: ' . $contact[$lang] . '?error=1'); exit; }

$subject = '=?UTF-8?B?' . base64_encode('Website enquiry: ' . $name) . '?=';
$body = "Name: $name\nPhone: $phone\nEmail: " . ($email ?: '-') . "\nType of work: $type\nLanguage of page: $lang\n\n$msg\n";
$headers = "From: MCC Group Website <$from>\r\n";
if ($email !== '') { $headers .= "Reply-To: $email\r\n"; }
$headers .= "Content-Type: text/plain; charset=UTF-8\r\nMIME-Version: 1.0\r\n";

if (@mail($to, $subject, $body, $headers)) { header('Location: ' . $thanks[$lang]); }
else { header('Location: ' . $contact[$lang] . '?error=1'); }
exit;
