import pont
from pont.client.world.entities.player import CombatClass, Gender
from pont.client.world.guid import Guid
from pont.client.world.guild.events import GuildEventType
from pont.client.world.guild.member import MemberStatus


def test_CMSG_GUILD_QUERY():
	data = bytes.fromhex('00065400000001000000')
	packet = pont.client.world.net.packets.CMSG_GUILD_QUERY.parse(data)
	assert packet.header.size == 6
	assert packet.guild_id == 1
	print(packet)

def test_SMSG_GUILD_QUERY_RESPONSE():
	data = bytes.fromhex('00635500010000004361727065204B696E64657267617274656E004775696C64204D6173746572004F666669636572005665746572616E004D656D62657200496E697469617465000000000000000000000000000000000000000000000000000005000000')
	packet = pont.client.world.net.packets.SMSG_GUILD_QUERY_RESPONSE.parse(data)
	print(packet)

	assert packet.header.size == 99
	assert packet.guild_id == 1
	assert packet.name == 'Carpe Kindergarten'
	ranks = list(packet.ranks)
	try:
		while True:
			ranks.remove('')
	except ValueError:
		pass

	assert ranks == ['Guild Master', 'Officer', 'Veteran', 'Member', 'Initiate']
	assert packet.emblem_style == 0
	assert packet.emblem_color == 0
	assert packet.border_style == 0
	assert packet.border_color == 0
	assert packet.num_ranks == 5

# def test_SMSG_

def test_SMSG_GUILD_ROSTER():
	data = bytes.fromhex('03BE8A001400000068656C6C6F206272617465000005000000FFF11D00FFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFF11D000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000043000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005000000000000000041646964690004000000FF0200210000005054A3410000130000000000000000466C6F72796E656C0004000000C80200210000002A0BB541000001000000000000000141637400000000005009006A0200000000120000000000000000466C79650004000000C8090021000000B8D9B44100000C00000000000000005368656C6C0004000000C808002100000051196941000016000000000000000052656473706F74646F776E0004000000FF0200210000008635AB4100000B0000000000000000456C696D696E650004000000FF02002100000092BAB34100001C0000000000000000436C65700004000000FF040021000000EE749B410000140000000000000000477269640004000000FF010021000000850BB44100001500000000000000004C796C6C610004000000CE02002100000022629C4100000700000000000000004C75636B790001000000CB01002100000008F49341000018000000000000000052656E64657A0004000000510500210000000070B1410000170000000000000000506F726E6875620004000000FF010021000000CC8DB34100000D00000000000000004B69640004000000C8010021000000073AAC4100000E0000000000000000476E6F6D65736F6D650004000000CA040021000000780CB5410000190000000000000000436C657069630004000000FF0100EF050000F002AC4100000F00000000000000004D616C660004000000C8040021000000B0D03D4100001B000000000000000050657273697374656E63650004000000FF0500210000000FD8AB4100001000000000000000004761696C69730004000000FF0400210000007BE9A24100001100000000000000004B617468656C0004000000FF010021000000C3FAAB410000')
	packet = pont.client.world.net.packets.SMSG_GUILD_ROSTER.parse(data)
	print(packet)

	assert packet.header.size == 958
	assert packet.total_members == 20
	assert packet.motd == 'hello brate'
	assert packet.guild_info == ''

	adidi = packet.members[0]
	assert adidi.guid == Guid(counter=5)
	assert adidi.status == MemberStatus.offline
	assert adidi.name == 'Adidi'
	assert adidi.rank_id == 4
	assert adidi.level == 255
	assert adidi.combat_class == CombatClass.paladin
	assert adidi.gender == Gender.male
	assert adidi.area_id == 33
	assert adidi.note == ''
	assert adidi.officer_note == ''

	florynel = packet.members[1]
	assert florynel.guid == Guid(counter=0x13)
	assert florynel.status == MemberStatus.offline
	assert florynel.name == 'Florynel'
	assert florynel.rank_id == 4
	assert florynel.level == 200
	assert florynel.combat_class == CombatClass.paladin
	assert florynel.gender == Gender.male
	assert florynel.area_id == 33
	assert florynel.note == ''
	assert florynel.officer_note == ''

	act = packet.members[2]
	assert act.guid == Guid(counter=1)
	assert act.status == MemberStatus.online
	assert act.name == 'Act'
	assert act.rank_id == 0
	assert act.level == 80
	assert act.combat_class == CombatClass.warlock
	# assert act.gender == Gender.female
	assert act.area_id == 618
	assert act.note == ''
	assert act.officer_note == ''

	data2 = bytes.fromhex('03D88A001500000068656C6C6F206272617465000005000000FFF11D00FFFFFFFF000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFF11D00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000430000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000043000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001F000000000000000145636F0001000000500400EF050000000018000000000000000052656E64657A000400000051050021000000DFFCC94100000D00000000000000004B69640004000000C8010021000000E6C6C4410000170000000000000000506F726E6875620004000000FF010021000000AB1ACC4100000C00000000000000005368656C6C0004000000C808002100000087198D4100001000000000000000004761696C69730004000000FF0400210000005A76BB4100001B000000000000000050657273697374656E63650004000000FF050021000000EE64C44100000F00000000000000004D616C660004000000C80400210000006EEA6E4100001C0000000000000000436C65700004000000FF040021000000CD01B44100000B0000000000000000456C696D696E650004000000FF0200210000007147CC4100000E0000000000000000476E6F6D65736F6D650004000000CA0400210000005799CD410000190000000000000000436C657069630004000000FF0100EF050000CF8FC44100001100000000000000004B617468656C0004000000FF010021000000A287C4410000120000000000000000466C79650004000000C80900210000009766CD4100000100000000000000014163740000000000500900EF0500000000130000000000000000466C6F72796E656C0004000000C80200210000000998CD41000005000000000000000041646964690004000000FF0200210000002FE1BB41000016000000000000000052656473706F74646F776E0004000000FF02002100000065C2C3410000140000000000000000477269640004000000FF0100210000006498CC4100000700000000000000004C75636B790001000000CB010021000000E780AC4100001500000000000000004C796C6C610004000000CE02002100000001EFB4410000')
	packet2 = pont.client.world.net.packets.SMSG_GUILD_ROSTER.parse(data2)
	print(packet2)

def test_SMSG_GUILD_EVENT():
	data = bytes.fromhex('000B9200020161797979797900')
	packet = pont.client.world.net.packets.SMSG_GUILD_EVENT.parse(data)
	print(packet)

	assert packet.header.size == 11
	assert packet.type == GuildEventType.motd
	assert packet.parameters[0] == 'ayyyyy'
	assert packet.guid is None

	data = bytes.fromhex('00109200020168656C6C6F20627261746500')
	packet = pont.client.world.net.packets.SMSG_GUILD_EVENT.parse(data)
	print(packet)

	assert packet.header.size == 16
	assert packet.type == GuildEventType.motd
	assert packet.parameters[0] == 'hello brate'
	assert packet.guid is None

	data = b'\x00\x11\x92\x00\r\x01Pont\x000\x00\x00\x00\x00\x00\x00\x00'
	packet = pont.client.world.net.packets.SMSG_GUILD_EVENT.parse(data)

	assert packet.header.size == 17
	assert packet.type == GuildEventType.signed_off
	assert packet.parameters == ['Pont']
	assert packet.guid == Guid(0x30)

# type = GuildEventType.signed_off
# parameters = ListContainer:
# Pont
# guid = 0x30, GuidType.player

def test_SMSG_GUILD_INVITE():
	data = b'\x00\x19\x83\x00Act\x00Carpe Kindergarten\x00'
	packet = pont.client.world.net.packets.SMSG_GUILD_INVITE.parse(data)
	print(packet)

	assert packet.header.size == 25
	assert packet.inviter == 'Act'
	assert packet.guild == 'Carpe Kindergarten'
