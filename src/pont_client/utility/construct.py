import ipaddress
import construct
from typing import Tuple, Union

def FixedString(length, encoding='ascii'):
	return construct.StringEncoded(construct.FixedSized(length, construct.GreedyBytes), encoding)

def RC4Encrypted(subcon, encrypt, decrypt, size):
	return construct.Transformed(subcon, decrypt, size, encrypt, size)

class UpperCString(construct.Adapter):
	def __init__(self, encoding='ascii'):
		super().__init__(construct.CString(encoding))
		self.encoding = encoding

	def _decode(self, obj: str, context, path) -> str:
		return obj.upper()

	def _encode(self, obj: str, context, path) -> str:
		return obj.upper()

class UpperPascalStringAdapter(construct.StringEncoded):
	def __init__(self, subcon, encoding):
		super().__init__(subcon, encoding)

	def _decode(self, obj, context, path):
		length = obj[0]
		return obj[1:length + 1].decode(self.encoding).upper()

	def _encode(self, obj, context, path):
		obj = obj.upper()
		return bytes([len(obj)]) + obj.encode(self.encoding)

UpperPascalString = lambda encoding='ascii': UpperPascalStringAdapter(construct.GreedyBytes, encoding=encoding)

class PaddedStringByteSwappedAdapter(construct.StringEncoded):
	def __init__(self, length, encoding='ascii'):
		super().__init__(construct.Bytes(length), encoding=encoding)
		self.length = length

	def _encode(self, obj: str, context, path) -> bytes:
		bs = bytes(reversed(obj.encode(self.encoding)))
		result = bs + bytes([0] * (self.length - len(bs)))
		return result

	def _decode(self, obj: bytes, context, path) -> str:
		subobj = obj[:self.length]
		subobj = bytes(reversed(subobj.replace(b'\x00', b'')))
		result = subobj.decode(self.encoding)
		return result

PaddedStringByteSwapped = PaddedStringByteSwappedAdapter

class AddressPort(construct.Adapter):
	def __init__(self, encoding='ascii', separator=':'):
		super().__init__(construct.CString(encoding))
		self.separator = separator
		self.encoding = encoding

	def _encode(self, obj: Union[Tuple[str, int], str], context, path) -> str:
		if type(obj) == str:
			ip, port = obj.split(self.separator)
		else:
			ip, port = obj

		addr_string = f'{ip}{self.separator}{port}'
		return addr_string

	def _decode(self, obj: str, context, path) -> Tuple[str, int]:
		ip, port = obj.split(self.separator)
		return ip, int(port)

class IPAddressAdapter(construct.Adapter):
	def _decode(self, obj, context, path):
		# TODO: Fix for v6
		ip = '.'.join(map(str, obj))
		return str(ipaddress.ip_address(ip))

	def _encode(self, obj, context, path):
		return ipaddress.ip_address(obj).packed

IPv4Address = IPAddressAdapter(construct.Bytes(4))
# IPv6Address = IPAddressAdapter(construct.Byte[16])

class ConstructEnumAdapter(construct.Enum):
	def __init__(self, enum_type, subcon, *merge, **mapping):
		super().__init__(subcon, *merge, **mapping)
		self.enum_type = enum_type

	def _decode(self, obj, context, path):
		return self.enum_type(super()._decode(obj, context, path))

	def _encode(self, obj, context, path):
		try:
			obj = obj.value
		except AttributeError:
			pass

		if isinstance(obj, Tuple):
			obj = obj[0]

		return super()._encode(int(obj), context, path)

PackEnum = lambda enum_type, subcon=construct.Byte: ConstructEnumAdapter(enum_type=enum_type, subcon=subcon)

class VersionStringFromBytesAdapter(construct.StringEncoded):
	def __init__(self, num_bytes, encoding='ascii'):
		super().__init__(construct.Bytes(length=num_bytes), encoding)

	def _decode(self, obj: bytes, context, path):
		return '.'.join([str(b) for b in obj])

	def _encode(self, obj: str, context, path):
		return bytes(list(map(int, obj.split('.'))))

VersionString = VersionStringFromBytesAdapter

Coordinates = lambda float_con = construct.Float32b: construct.Struct(
	'x' / float_con,
	'y' / float_con,
	'z' / float_con,
)