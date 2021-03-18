import kubernetes


class SecretBinding:
  def __init__(self, name, namespace, service_account, secrets, target = None, template = None):
    self.__name = name
    self.__namespace = namespace
    self.__service_account = service_account
    self.__secrets = secrets
    self.__target = target if target is not None else f"/esk/secrets/{ name }"
    self.__template = template


  def compare_spec(self, spec):
    '''
      Compare a spec with self.spec, return true if the same
    '''
  
    return self.__target == spec.get('target') and self.__template == spec.get('template')


  def to_k8s_resources(self):
    '''
      Transform this binding to a kubernetes role and role binding
    '''

    role = kubernetes.client.V1Role(
      metadata = kubernetes.client.V1ObjectMeta(
        name = self.__name,
        namespace = self.__namespace
      ),
      rules = [
        kubernetes.client.V1PolicyRule(
          api_groups = ['esk.io'],
          resources = ['externalsecrets'],
          resource_names = [ s.get('name') for s in self.__secrets ],
          verbs = ['get']
        ),
        kubernetes.client.V1PolicyRule(
          api_groups = ['esk.io'],
          resources = ['secretbindings'],
          resource_names = [self.__name],
          verbs = ['get']
        )
      ]
    )

    role_binding = kubernetes.client.V1RoleBinding(
      role_ref = kubernetes.client.V1RoleRef(
        api_group = 'rbac.authorization.k8s.io',
        kind = 'Role',
        name = self.__name
      ),
      metadata = kubernetes.client.V1ObjectMeta(
        name = self.__name,
        namespace = self.__namespace
      ),
      subjects = [
        kubernetes.client.V1Subject(
          kind = 'ServiceAccount',
          name = self.__service_account,
          namespace = self.__namespace
        )
      ]
    )

    return role, role_binding


  def get_spec(self):
    return {
      'serviceAccount': self.__service_account,
      'secrets': self.__secrets,
      'target': self.__target,
      'template': self.__template
    }


  def get_namespace(self):
    return self.__namespace


  def get_name(self):
    return self.__name


  def get_target(self):
    return self.__target


  def get_template(self):
    return self.__template