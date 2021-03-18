import json

class InitContainer:
  def __init__(self, name, image, processor_addr):
    self.__name = name
    self.__image = image
    self.__env = [
      {
        'name': 'PROCESSOR_ADDR',
        'value': processor_addr
      }
    ]
    self.__vol_mounts = []
    self.__volumes = []


  def append_volumes_for_bind(self, bind):
    '''
      Get Volume and VolumeMount for a bind, returned in that order as a tuple
    '''

    self.__vol_mounts.append(
      {
        "name": f"esk-secrets-{ bind.get('name') }",
        "mountPath": '/'.join(bind.get('target').split('/')[0:-1])
      })

    self.__volumes.append({
      'name': f"esk-secrets-{ bind.get('name') }",
      'emptyDir': {}
    })

  def get_volumes(self):
    return self.__volumes

  def add_bind(self, bind, namespace, spec):
    self.append_volumes_for_bind(bind)
    self.__env.append({
      'name': f"BIND_{ bind.get('name') }",
      'value': json.dumps({
        'name': bind.get('name'),
        'namespace': namespace,
        'secrets': ','.join([ s.get('name') for s in spec.get('secrets') ]),
        'target': bind.get('target'),
        'template': bind.get('template')
      })
    })

  def get(self):
    return {
      "name": self.__name,
      "image": self.__image,
      'imagePullPolicy': 'Always',
      "env": self.__env,
      "volumeMounts": self.__vol_mounts
    }