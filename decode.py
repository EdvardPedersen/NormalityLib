# Trying to read normality game files
import argparse
import logging
import numpy as np
import ndt
import os

def hexify(string):
  return ":".join("{:02x}".format(ord(c)) + "(" + c + ")"  for c in string)

class CompressedFile:
  def __init__(self, filename):
    self.filename = filename
    self.f = open(filename)
    self.data = np.fromfile(filename, np.uint8)
    self.d_data = []
    
  def save(self):
    filename,_ = os.path.splitext(self.filename)
    np.save(filename, self.d_data)
    
  def load(self):
    self.d_data = np.load(self.filename)
    
  def print_header(self):
    header = self.d_data[1:37].view(ndt.header)
    print header["header"]
    palettes = self.d_data[header["addr_palette"]:header["addr_palette"] + (256*3)].view(ndt.palettes)
    print palettes
    
  def decompress(self):
    output = []
    pos = 0
    d = self.data
    while pos < len(d):
      b = d[pos]
      pos += 1
      if b == 0:
        break
      if(b >= 0xE0):
        logging.info("Case 1")
        b2 = d[pos]
        pos += 1
        b3 = d[pos]
        pos += 1
        offset = ((b - 0xE0) * 256) + b2 + 3
        length = b3 + 5
        output.extend(self._reuse_bytes(output,offset,length))
      elif b >= 0xC0:
        logging.info("Case 2")
        b2 = d[pos]
        pos += 1
        offset = ((b % 4) * 256) + b2 + 3
        length = 4 + (b - 0xC0) // 4
        output.extend(self._reuse_bytes(output,offset, length))
      elif b >= 0x80:
        logging.info("Case 3")
        offset = (b - 0x80) + 3
        output.extend(self._reuse_bytes(output,offset, 3))
      elif b >= 0x70:
        logging.info("Case 4")
        reps = (b - 0x70) + 2
        output.extend(self._reuse_bytes(output,2, 2, reps))
      elif b >= 0x60:
        logging.info("Case 5")
        reps = (b - 0x60) + 3
        output.extend(self._reuse_bytes(output,1, 1, reps))
      elif b >= 0x50:
        logging.info("Case 6")
        length = (b - 0x50) + 2
        s = output[-2]
        e = output[-1]
        step = int(e) - int(s)
        for x in range(1,length+1):
          next_num = e + step * x
          output.append(0)
          output.append(next_num)
      elif b >= 0x40:
        logging.info("Case 7")
        length = (b - 0x40) + 3
        s = output[-2]
        e = output[-1]
        step = int(e) - int(s)
        for x in range(1,length+1):
          next_num = e + step * x
          output.append(next_num)
      else:
        logging.info("DEFAULT CASE")
        output.extend(d[pos-1:pos+b-1])
        pos += b
    self.d_data = np.array(output, np.uint8)
        
  def _reuse_bytes(self,input,offset,length,repeats=1):
    return (input[-offset:] * ((length//len(input[-offset:]))+1))[:length] * repeats

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  
  parser.add_argument('-i', dest='input_file', help="Input file", required=True)
  parser.add_argument('-d', dest='debug', action="store_const", const=True, help="Enable debugging output", default=False)
  
  args = parser.parse_args()
  
  if(args.debug):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)
  
  c = CompressedFile(args.input_file)
  (filename, extension) = os.path.splitext(args.input_file)
  if(extension == ".MGL"):
    c.decompress()
    c.save()
  else:
    c.load()
  c.print_header()
