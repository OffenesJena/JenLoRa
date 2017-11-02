function Decoder(bytes, port) {
  
  // Decode an uplink message from a buffer
  // (array) of bytes to an object of fields.
  var decoded = {};

  var field = 0;
  decoded.temp  = '';
  decoded.hum   = '';
  decoded.press = '';
  decoded.pm10  = '';
  decoded.pm25  = '';
  readunit      = false;
  
  for (var i = 0; i < bytes.length; i++)
  {
    
    if (bytes[i] == 0x3B)   // ' ' is our separator
    {
      field++;
      readunit = false;
      continue;
    }
    
    if ((bytes[i] != 0x2E) &&                              // '.' is good!
        (bytes[i] < 0x30 || bytes[i] > 0x39 || readunit))  // everything except numbers are bad!
    {
      readunit = true;
      continue;
    }
    
    switch (field)
    {
      case 0: decoded.temp  += String.fromCharCode(bytes[i]); break;
      case 1: decoded.hum   += String.fromCharCode(bytes[i]); break;
      case 2: decoded.press += String.fromCharCode(bytes[i]); break;
      case 3: decoded.pm10  += String.fromCharCode(bytes[i]); break;
      case 4: decoded.pm25  += String.fromCharCode(bytes[i]); break;
    }
  }

  decoded.temp  = parseFloat(decoded.temp);
  decoded.hum   = parseFloat(decoded.hum);
  decoded.press = parseFloat(decoded.press);
  decoded.pm10  = parseFloat(decoded.pm10);
  decoded.pm25  = parseFloat(decoded.pm25);

  return decoded;
  
}
