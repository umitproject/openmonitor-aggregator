class splitedDat:
	def __init__(self, filename):
		idx = open(filename + '.idx',"r")
		line=idx.readline()
		self.filesize=0
		self.chunks=[]
		
		while line != "":
			ldata=line.strip().split(":")
			id=int(ldata[0])
			start=int(ldata[1])
			end=int(ldata[2])
			size=int(ldata[3])
			line=idx.readline()
			
			self.filesize += size
			
			self.chunks.append({"id":id,"start":start,"end":end,"size":size,"file":open("%s.%d" % (filename,id),"rb")})

		self.filepos=0

	def readChunk(self,start,length):
		end=start+length
		left=length
		data=''
		
		for chunk in self.chunks:
			plik=chunk["file"]
			if start >= chunk["start"]  and start < chunk["end"]:
				if end >= chunk["end"]:
					cstart=start-chunk['start']
					clen=chunk['end']-start
					plik.seek(cstart,0)
					data = plik.read(clen)
				else:
					cstart=start-chunk['start']
					plik.seek(cstart,0)
					data = plik.read(length)
			elif start < chunk["start"] and end >= chunk["start"]:
				clen=end-chunk['start']
				plik.seek(0,0)
				data += plik.read(clen)
				
		return data
		
	def read(self,size):
		start=self.filepos
		readed=self.readChunk(start,size)
		lreaded = len(readed)
		self.filepos=start+size
		return readed
		
	def seek(self,offset,direction):
		if direction == 0:
			self.filepos = offset
		elif direction == 1:
			self.filepos += offset
		elif direction == 2:
			self.filepos = self.filesize + offset
		else:
			print "ERRRRRRROR"
			rc=-1
		return
		
	def tell(self):
		return self.filepos
		
	def close(self):
		return self.file.close()