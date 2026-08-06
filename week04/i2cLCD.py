from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(
	i2c_expander='PCF8574',
	address=0x27,
	port=1,
	cols=16,
	rows=2,
	charmap='A00',
	auto_linebreaks=True,
	backlight_enabled=True
)

lcd.write_string("Yossaphol")
lcd.crlf() #new line
lcd.write_string("67070145")