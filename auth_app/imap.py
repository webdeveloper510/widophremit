
# Create and initialize IMAP client
client = ImapClient("australia1.rebel.com", 465, "service@remitassure.com", "@Satisfy2020")

# Set security options
client.security_options = SecurityOptions.SSLIMPLICIT