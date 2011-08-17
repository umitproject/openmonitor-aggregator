from django.db import models
#from Crypto.PublicKey import RSA
#from Crypto import Random


class Agent(models.Model):
    agentID       = models.AutoField(primary_key=True)
    agentType     = models.CharField(max_length=10)
    agentVersion  = models.PositiveIntegerField()
    registered_at = models.DateTimeField(auto_now_add=True)
    registered_ip = models.CharField(max_length=255)
    publicKey     = models.TextField()

    def create(versionNo, agentType, ip, publicKey):
        agent = Agent()
        agent.agentVersion = versionNo
        agent.agentType = agentType
        agent.registered_ip = ip
        agent.publicKey = publicKey
        agent.save()
        return agent

    def generateKeyPair(null):
        #rng = Random.new().read
        #RSAkey = RSA.generate(1024, rng)
        #k = RSAkey.exportKey()
        #return k
        pass

    def __unicode__(self):
        return "Agent %s (%s %s) - %s - %s" % (self.agentID, self.agentType, self.agentVersion, self.registered_at, self.registered_ip)

    create = staticmethod(create)
    generateKeyPair = staticmethod(generateKeyPair)