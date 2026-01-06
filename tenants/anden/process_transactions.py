import subprocess
import json
import re

transaction_ids = ["33706","33679","33652","33647","33646","33644","33636","33615","33613","33610","33567","33562","33552","33548","33539","33532","33529","33494","33440","33434","33402","33401","33382","33365"]

transactions = []
errors = []

for email_id in transaction_ids:
    try:
        result = subprocess.run(
            ['python', 'execution/gmail_read.py'],
            input=json.dumps({"email_id": email_id}),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            body = data['email']['body']
            email_date = data['email']['date']
            
            amount_match = re.search(r'Amount: \$ ([0-9.]+)', body)
            merchant_match = re.search(r'Merchant Name: ([^\r\n<]+)', body)
            date_match = re.search(r'Date: ([^\r\n<]+)', body)
            time_match = re.search(r'Time: ([^\r\n<]+)', body)
            category_match = re.search(r'Merchant Category Description: ([^\r\n<]+)', body)
            
            if amount_match and merchant_match:
                transactions.append({
                    'email_date': email_date,
                    'date': date_match.group(1) if date_match else email_date[:10],
                    'time': time_match.group(1) if time_match else "",
                    'amount': float(amount_match.group(1)),
                    'merchant': merchant_match.group(1).strip(),
                    'category': category_match.group(1).strip() if category_match else "Unknown"
                })
    except Exception as e:
        errors.append(f"Error processing {email_id}: {str(e)}")

# Sort by date
transactions.sort(key=lambda x: (x['date'], x['time']))

# Calculate totals
total_spent = sum(t['amount'] for t in transactions)
total_count = len(transactions)

# Category breakdown
categories = {}
for trans in transactions:
    cat = trans['category']
    if cat not in categories:
        categories[cat] = {'count': 0, 'total': 0.0, 'transactions': []}
    categories[cat]['count'] += 1
    categories[cat]['total'] += trans['amount']
    categories[cat]['transactions'].append(trans)

print(json.dumps({
    'transactions': transactions,
    'total_spent': total_spent,
    'total_count': total_count,
    'categories': categories,
    'errors': errors
}, indent=2))
