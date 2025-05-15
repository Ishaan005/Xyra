from weasyprint import HTML, CSS
from jinja2 import Template

def render_invoice_html(invoice, organization, line_items):
    # You can move this template to a separate HTML file for easier editing
    template_str = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background: #222; color: #fff; padding: 20px; }
            .section { margin: 20px 0; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #eee; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Invoice {{ invoice.invoice_number }}</h1>
            <p>Organization: {{ organization.name }}</p>
            <p>Issue Date: {{ invoice.issue_date.strftime('%Y-%m-%d') }}</p>
            <p>Due Date: {{ invoice.due_date.strftime('%Y-%m-%d') }}</p>
        </div>
        <div class="section">
            <h2>Line Items</h2>
            <table>
                <tr>
                    <th>Description</th><th>Quantity</th><th>Unit Price</th><th>Amount</th>
                </tr>
                {% for item in line_items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.unit_price }}</td>
                    <td>{{ item.amount }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div class="section">
            <strong>Total: ${{ invoice.total_amount }}</strong>
        </div>
    </body>
    </html>
    """
    template = Template(template_str)
    return template.render(invoice=invoice, organization=organization, line_items=line_items)


def generate_invoice_pdf(invoice, organization, line_items, output_path):
    html_str = render_invoice_html(invoice, organization, line_items)
    HTML(string=html_str).write_pdf(output_path)
    return output_path
