import re
from mrjob.job import MRJob 

class PredictBySlopeOne(MRJob):
    # first step, generate user-item table, input is the train.txt and the predict predict.txt
    def mapper1(self, _, line):
        item = line.split()
        if len(item) > 2:
            yield item[0],(item[1],item[2])
        elif(len(item) == 2):
            yield item[0],(item[1],-1)
        
    def reducer1(self,key,value):
        for v in value:
            yield key,v  
            
    def reducer2(self,key,value):
        rateM={}
        preM=[]
        for movieid,rate in value:
            if rate==-1.0:
                preM.append(movieid)
            else:
                rateM[movieid]=rate
                
        for i,itemi in enumerate(rateM.iterkeys()):
            for j,itemj in enumerate(rateM.iterkeys()):
                if j<=i :continue
                if itemi>itemj:
                    yield (itemi,itemj),(key,float(rateM[itemi])-float(rateM[itemj]),-1)
                else:
                    yield (itemj,itemi),(key,float(rateM[itemj])-float(rateM[itemi]),-1)
                

        for rm,rate in rateM.iteritems():
            for pm in preM:
                if rm>pm:
                    yield (rm,pm),(key,rate,1)   # the second is the one to be predicted
                else:
                    yield (pm,rm),(key,rate,0)   # the first is the one to be predicted
                    
    
    def reducer3(self,key,value):
        total=0
        fre=0
        needPredict=[]
        for userId,diff,flag in value:
            if flag!=-1:
                #yield key,(userId,diff,flag)
                needPredict.append((userId,float(diff),flag))
            else:
                total+=float(diff)
                fre+=1
                
        if fre>0 and len(needPredict)>0:
            avg=total/fre
            for userId,rate,flag in needPredict:
                if float(flag)==0:
                    predictRate=avg+rate
                    mp=key[0]
                else:
                    predictRate=rate-avg
                    mp=key[1]
                    print userId, mp, predictRate, fre
                yield (userId,mp),(predictRate,fre)
            
            
    def reducer4(self,key,value):
        totalFre=0
        totalRate=0
        for predictRate,fre in value:
            totalRate+=predictRate*fre
            totalFre+=fre
        yield key,totalRate/totalFre
            
                          

    def steps(self):
        return [self.mr(mapper=self.mapper1,combiner=self.reducer1,reducer=self.reducer1),
                self.mr(reducer=self.reducer2),
                self.mr(reducer=self.reducer3),
                self.mr(reducer=self.reducer4)]


if __name__=="__main__":
    PredictBySlopeOne.run()
