from weasyprint import HTML, CSS
from jinja2 import Template
import json

def render_invoice_html(invoice, organization, line_items):
    # Enhanced template with better formatting for different billing models
    template_str = """
    <html>
    <head>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                color: #333; 
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: #fff; 
                padding: 30px; 
                border-radius: 8px;
                margin-bottom: 30px;
            }
            .header h1 { 
                margin: 0 0 10px 0; 
                font-size: 2.2em; 
                font-weight: 300; 
            }
            .header p { 
                margin: 5px 0; 
                font-size: 1.1em; 
                opacity: 0.9; 
            }
            .section { 
                margin: 30px 0; 
                background: #fff; 
                border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                overflow: hidden; 
            }
            .section h2 { 
                background: #f8f9fa; 
                margin: 0; 
                padding: 20px; 
                border-bottom: 1px solid #dee2e6; 
                color: #495057; 
                font-size: 1.5em; 
                font-weight: 500; 
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 0; 
            }
            th, td { 
                padding: 15px; 
                text-align: left; 
                border-bottom: 1px solid #dee2e6; 
            }
            th { 
                background: #f8f9fa; 
                font-weight: 600; 
                color: #495057; 
                font-size: 0.9em; 
                text-transform: uppercase; 
                letter-spacing: 0.5px; 
            }
            tr:hover { 
                background: #f8f9fa; 
            }
            .amount { 
                text-align: right; 
                font-weight: 600; 
            }
            .total-section { 
                background: #f8f9fa; 
                padding: 25px; 
                border-radius: 8px; 
                text-align: right; 
                margin-top: 20px; 
            }
            .total-amount { 
                font-size: 1.8em; 
                font-weight: 700; 
                color: #28a745; 
                margin: 10px 0; 
            }
            .metadata { 
                font-size: 0.85em; 
                color: #6c757d; 
                font-style: italic; 
            }
            .billing-details {
                font-size: 0.9em;
                color: #6c757d;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Invoice {{ invoice.invoice_number }}</h1>
            <p><strong>Organization:</strong> {{ organization.name }}</p>
            <p><strong>Issue Date:</strong> {{ invoice.issue_date.strftime('%B %d, %Y') }}</p>
            <p><strong>Due Date:</strong> {{ invoice.due_date.strftime('%B %d, %Y') }}</p>
            <p><strong>Status:</strong> {{ invoice.status.title() }}</p>
        </div>
        
        <div class="section">
            <h2>Billing Details</h2>
            <table>
                <tr>
                    <th style="width: 40%;">Description</th>
                    <th style="width: 15%;">Quantity</th>
                    <th style="width: 20%;">Unit Price</th>
                    <th style="width: 20%;">Amount</th>
                    <th style="width: 5%;">Type</th>
                </tr>
                {% for item in line_items %}
                <tr>
                    <td>
                        <strong>{{ item.description }}</strong>
                        {% if item.item_metadata %}
                        <div class="billing-details">
                            {% set metadata = item.item_metadata if item.item_metadata is mapping else item.item_metadata|fromjson %}
                            {% if metadata.outcome_value %}
                                Total Outcome Value: ${{ "%.2f"|format(metadata.outcome_value) }}
                            {% endif %}
                            {% if metadata.outcome_count %}
                                Number of Outcomes: {{ metadata.outcome_count }}
                            {% endif %}
                            {% if metadata.percentage_fee and metadata.percentage_fee > 0 %}
                                Percentage-based Fee: ${{ "%.2f"|format(metadata.percentage_fee) }}
                            {% endif %}
                            {% if metadata.fixed_fee and metadata.fixed_fee > 0 %}
                                Fixed-charge Fee: ${{ "%.2f"|format(metadata.fixed_fee) }}
                            {% endif %}
                            {% if metadata.total_fee %}
                                Total Fee: ${{ "%.2f"|format(metadata.total_fee) }}
                            {% endif %}
                            {% if metadata.outcome_type %}
                                Outcome Type: {{ metadata.outcome_type }}
                            {% endif %}
                            {% if metadata.billing_period %}
                                <br>Billing Period: {{ metadata.billing_period }}
                            {% endif %}
                        </div>
                        {% endif %}
                    </td>
                    <td>{{ item.quantity }}</td>
                    <td class="amount">${{ "%.2f"|format(item.unit_price) }}</td>
                    <td class="amount">${{ "%.2f"|format(item.amount) }}</td>
                    <td>
                        <span class="badge">{{ item.item_type.title() }}</span>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="total-section">
            {% if invoice.tax_amount and invoice.tax_amount > 0 %}
            <p><strong>Subtotal:</strong> ${{ "%.2f"|format(invoice.amount) }}</p>
            <p><strong>Tax:</strong> ${{ "%.2f"|format(invoice.tax_amount) }}</p>
            {% endif %}
            <div class="total-amount">
                <strong>Total: ${{ "%.2f"|format(invoice.total_amount) }}</strong>
            </div>
            <p class="metadata">Currency: {{ invoice.currency or 'USD' }}</p>
            {% if invoice.notes %}
            <p class="metadata">Notes: {{ invoice.notes }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    """
    template = Template(template_str)
    # Add the custom fromjson filter
    template.environment.filters['fromjson'] = lambda x: json.loads(x) if isinstance(x, str) else x
    return template.render(invoice=invoice, organization=organization, line_items=line_items)


def generate_invoice_pdf(invoice, organization, line_items, output_path):
    html_str = render_invoice_html(invoice, organization, line_items)
    HTML(string=html_str).write_pdf(output_path)
    return output_path
