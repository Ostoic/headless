import construct

from pont.utility.construct import AddressPort, GuidUnpacker, PackedCoordinates, unpack_guid, pack_guid
from pont.client.world import Position
from pont.client.world.guid import Guid


def test_address_port():
	# Test big endian encoding and decoding
	con = AddressPort()
	address = ('127.0.0.1', 8085)
	address_packed = con.build(address)

	assert address_packed == b'127.0.0.1:8085\x00'
	assert ('127.0.0.1', 8085) == con.parse(address_packed)

def test_address_port2():
	# Test composability with other constructs
	addr_con = AddressPort()
	Test = construct.Sequence(
		construct.CString('ascii'),
		addr_con,
		construct.Int
	)

	data = Test.build(['hey there', ('127.0.0.1', 8085), 7])
	assert data  == b'hey there\x00127.0.0.1:8085\x00\x00\x00\x00\x07'
	assert Test.parse(data) == ['hey there', ('127.0.0.1', 8085), 7]

def test_packed_guid():
	guid = Guid(value=0x7000000003372cc)

	print(guid)
	print(Guid(value=unpack_guid(*pack_guid(guid.value))))
	assert unpack_guid(*pack_guid(guid.value)) == guid.value

	packed_guid = GuidUnpacker(Guid).build(guid)
	parsed_guid = GuidUnpacker(Guid).parse(packed_guid)
	assert parsed_guid == guid

def test_packed_coordinates():
	pos = Position(2.1, -33, 99.8)
	data = PackedCoordinates(Position).build(pos)
	packet = PackedCoordinates(Position).parse(data)
	print(packet)

	assert packet.x == 2
	assert packet.y == (2**9 - 33) # Can't distinguish between negatives it seems
	assert packet.z == 99.75
