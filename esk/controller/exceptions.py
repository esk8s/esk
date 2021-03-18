
class ESKException(Exception):
  def __init__(self, status_code, message):
    self.status = status_code
    self.message = message

  def __str__(self) -> str:
      return f"{ self.status }: { self.message }"