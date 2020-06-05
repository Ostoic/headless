import traceback
import trio

from pont_client import client as pont, cryptography
from pont_client.client import auth, ClientState
from pont_client.client.auth import AuthState, RealmType, RealmStatus
from pont_client.utility.string import bytes_to_int
from tests.cryptography.test_srp import load_test_servers

logins_filename = 'C:/Users/dinne/Documents/Projects/pont/servers_config.json'
test_servers = load_test_servers(logins_filename)
tc_login = test_servers['trinity-core-3.3.5']['account']

async def auth_server(stream):
	try:
		protocol = auth.net.AuthProtocol(stream)
		challenge_request = await protocol.receive_challenge_request()
		print(challenge_request)

		assert challenge_request.packet_size == 34 + len(challenge_request.account_name)
		assert challenge_request.game == 'WoW'
		assert challenge_request.version == '3.3.5'
		assert challenge_request.build == 12340

		generator = 7
		prime = 62100066509156017342069496140902949863249758336000796928566441170293728648119
		server_public = 29690934590145573207593128186052252288614061230055487511226196652110486395787
		salt = 92090571083452222281680040879036827917433471144889767667508809381093896083463
		await protocol.send_challenge_response(
			generator=generator,
			prime=prime,
			server_public=server_public,
			salt=salt
		)

		proof_request = await protocol.receive_proof_request()
		client_private = 143386892073113346271045296825355365119602324795205856098132479049957622403427006810653616896639308669514885320513042624825577275523311345156882292579472806120577841118102290052948040847318515534261288049316514160095147951671405527775489066400222418481863631312167863930538967927022064010646095222765545969242

		srp = cryptography.srp.WowSrpClient(username=tc_login['username'], password=tc_login['password'], prime=prime, generator=generator, client_private=client_private)
		client_public, session_proof = srp.process(server_public=server_public, salt=salt)
		assert client_public == proof_request.client_public
		assert session_proof == proof_request.session_proof

		actual_session_proof_hash = 1022273791007009790071844123884488983605182042497
		assert bytes_to_int(srp.session_proof_hash) == actual_session_proof_hash

		await protocol.send_proof_response(session_proof_hash=actual_session_proof_hash)
		await protocol.receive_realmlist_request()

		realms = [auth.Realm.build({
			'type': RealmType.pvp,
			'status': RealmStatus.online,
			'name': 'PontCore',
			'address': '127.0.0.1:8085',
			'population': 0,
			'num_characters': 2
		})]

		await protocol.send_realmlist_response(realms=realms)

	except Exception:
		traceback.print_exc()

async def client_login(auth_address, stream):
	auth_debug = {'client_private': 143386892073113346271045296825355365119602324795205856098132479049957622403427006810653616896639308669514885320513042624825577275523311345156882292579472806120577841118102290052948040847318515534261288049316514160095147951671405527775489066400222418481863631312167863930538967927022064010646095222765545969242}

	async with pont.Client() as client:
		try:
			assert client.auth.state == AuthState.not_connected
			await client.auth.connect(auth_address, stream=stream)
			await client.auth.authenticate(tc_login['username'], tc_login['password'], debug=auth_debug)
			assert client.auth.state >= AuthState.logged_in

			realmlist = await client.auth.realmlist()
			assert client.auth.state == AuthState.realmlist_ready

			assert realmlist[0].type == RealmType.pvp
			assert realmlist[0].status == RealmStatus.online
			assert realmlist[0].name == 'PontCore'
			assert realmlist[0].address == '127.0.0.1:8085'
			assert realmlist[0].populaton == 0
			assert realmlist[0].num_characters == 2

		except Exception as e:
			traceback.print_exc()

async def test_auth_protocol():
	(client_stream, server_stream) = trio.testing.memory_stream_pair()
	auth_address = ('10.179.205.114', 3724)
	with trio.fail_after(2):
		async with trio.open_nursery() as nursery:
			nursery.start_soon(client_login, auth_address, client_stream)
			nursery.start_soon(auth_server, server_stream)