from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
from datetime import datetime

def generate_queue_ticket(queue_number, service_type):
    # Create PDF filename in current directory
    filename = f"ticket_{queue_number}.pdf"
    
    # Ensure we're in the right directory
    current_dir = os.getcwd()
    filepath = os.path.join(current_dir, filename)
    
    # Create PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Header with styling
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height-1*inch, "🎫 TICKET ANTRIAN")
    
    # Subtitle
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-1.5*inch, "Rumah Sakit/Puskesmas")
    
    # Queue details
    c.setFont("Helvetica", 20)
    c.drawCentredString(width/2, height-2.5*inch, "NOMOR ANTRIAN:")
    c.setFont("Helvetica-Bold", 60)
    c.drawCentredString(width/2, height-3.5*inch, queue_number)
    c.setFont("Helvetica", 20)
    c.drawCentredString(width/2, height-4.2*inch, f"Layanan: {service_type}")
    
    # Timestamp
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-5*inch, f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    
    # Footer
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, 1.2*inch, "Terima kasih telah menggunakan layanan kami")
    c.drawCentredString(width/2, 0.8*inch, "Silakan tunggu nomor antrian Anda dipanggil")
    
    c.save()
    
    print(f"PDF generated: {filepath}")
    return filepath