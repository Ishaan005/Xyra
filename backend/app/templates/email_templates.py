"""
Email templates used throughout the application.

This module contains functions that return HTML and text templates for various
email communications. Each function returns a template string with placeholders
that can be filled in with the format() method.

Templates are separated from the email sending logic to:
1. Keep the codebase more maintainable
2. Allow for easier template customization
3. Make testing more straightforward
4. Support potential future template localization
"""

def get_invoice_email_html_template() -> str:
    """
    Returns the HTML template for invoice emails
    """
    return """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; }
            .header { padding: 20px 0; border-bottom: 1px solid #eee; }
            .content { padding: 20px 0; }
            .footer { padding: 20px 0; border-top: 1px solid #eee; font-size: 12px; color: #777; }
            .button { display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .amount { text-align: right; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Invoice {invoice_number}</h2>
                <p>From: {organization_name}</p>
            </div>
            
            <div class="content">
                <p>Dear Customer,</p>
                
                <p>Please find attached invoice #{invoice_number} for your recent services.</p>
                
                {custom_message_html}
                
                <h3>Invoice Details:</h3>
                <p>
                    <strong>Invoice Number:</strong> {invoice_number}<br>
                    <strong>Issue Date:</strong> {issue_date}<br>
                    <strong>Due Date:</strong> {due_date}<br>
                    <strong>Total Amount:</strong> {currency} {total_amount}
                </p>
                
                {payment_info}
                
                <p>{pdf_message}</p>
            </div>
            
            <div class="footer">
                <p>Thank you for your business!</p>
                <p>{organization_name}</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_invoice_email_text_template() -> str:
    """
    Returns the plain text template for invoice emails
    """
    return """
    Invoice {invoice_number} from {organization_name}
    
    Dear Customer,
    
    Please find attached invoice #{invoice_number} for your recent services.
    
    {custom_message}
    
    Invoice Details:
    - Invoice Number: {invoice_number}
    - Issue Date: {issue_date}
    - Due Date: {due_date}
    - Total Amount: {currency} {total_amount}
    
    {pdf_message}
    
    {payment_link_text}
    
    Thank you for your business!
    {organization_name}
    """

def get_payment_button_html(payment_link: str) -> str:
    """
    Returns the HTML for the payment button section
    """
    return f"""
    <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 4px;">
        <p><strong>Payment Link:</strong></p>
        <p><a href="{payment_link}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Pay Invoice Now</a></p>
        <p style="font-size: 12px; color: #666;">This is a secure payment link that will allow you to pay your invoice using a credit card or other payment method.</p>
    </div>
    """

def get_custom_message_html(message: str) -> str:
    """
    Returns the HTML for a custom message section
    """
    if not message or not message.strip():
        return ""
        
    return f"""
    <div style="margin: 20px 0; padding: 10px; border-left: 4px solid #ccc;">
        <p>{message}</p>
    </div>
    """
