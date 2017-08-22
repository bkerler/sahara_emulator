'''
USB Class definitions for Qualcomm QDLoader 9008 Firehose
(c) B. Kerler 2017

At least set up hwid and hash.
serial and sbversion is optional for testing.
Supports extraction of firehose loaders, saves as [hwid].bin in local directory

'''
import struct
import binascii
import time
from six.moves.queue import Queue
from usb.usb_device import USBDevice
from usb.usb_configuration import USBConfiguration
from usb.usb_interface import USBInterface
from usb.usb_endpoint import USBEndpoint
from usb.usb_vendor import USBVendor
from usb.usb_class import USBClass

#z ultra c 6833 msm8974_23_4_aid_4
#hash = bytearray.fromhex("49109A8016C239CD8F76540FE4D5138C87B2297E49C6B30EC31852330BDDB177")
#hwid = 0x04000100E1007B00
#serial = 0x01678739
#sblversion = 0x00000000

#oneplus one 3t
hash = bytearray.fromhex("c0c66e278fe81226585252b851370eabf8d4192f0f335576c3028190d49d14d4")
serial = 0x8d3e01ed
hwid = bytearray.fromhex("B93D702AE1F00500")
sblversion = 0x00000002

#hash = b"\xCC\x31\x53\xA8\x02\x93\x93\x9B\x90\xD0\x2D\x3B\xF8\xB2\x3E\x02\x92\xE4\x52\xFE\xF6\x62\xC7\x49\x98\x42\x1A\xDA\xD4\x2A\x38\x0F"
#hash = bytearray.fromhex("1801000F43240892D02F0DC96313C81351B40FD5029ED98FF9EC7074DDAE8B05CDC8E1")
#hash = bytearray.fromhex("5A93232B8EF5567752D0CB5554835215D1C473502E6F1052A78A6715B8B659AA")

class USBSaharaVendor(USBVendor):
    name = 'SaharaVendor'

    def __init__(self, app, phy):
        super(USBSaharaVendor, self).__init__(app, phy)
        self.latency_timer = 0x01
        self.data = 0x00
        self.baudrate = 0x00
        self.dtr = 0x00
        self.flow_control = 0x00
        self.rts = 0x00
        self.dtren = 0x00
        self.rtsen = 0x00
        self.elfstart = 0x00
        self.reallen = 0x00
    def setup_local_handlers(self):
        self.local_handlers = {
           # 0x00: self.handle_reset,
        }

    def handle_reset(self, req):
        print("Got reset request")
        return b'aber'

    def handle_modem_ctrl(self, req):
        self.dtr = req.value & 0x0001
        self.rts = (req.value & 0x0002) >> 1
        self.dtren = (req.value & 0x0100) >> 8
        self.rtsen = (req.value & 0x0200) >> 9
        if self.dtren:
            self.info('DTR is enabled, value %d' % self.dtr)
        if self.rtsen:
            self.info('RTS is enabled, value %d' % self.rts)
        return b''

    def handle_set_flow_ctrl(self, req):
        self.flow_control = req.value
        if req.value == 0x000:
            self.info('SET_FLOW_CTRL to no handshaking')
        if req.value & 0x0001:
            self.info('SET_FLOW_CTRL for RTS/CTS handshaking')
        if req.value & 0x0002:
            self.info('SET_FLOW_CTRL for DTR/DSR handshaking')
        if req.value & 0x0004:
            self.info('SET_FLOW_CTRL for XON/XOFF handshaking')
        return b''

    def handle_set_baud_rate(self, req):
        self.dtr = req.value & 0x0001
        self.baudrate = req.value
        self.info('baudrate set to: %#x dtr set to: %#x' % (self.baudrate, self.dtr))
        return b''

    def handle_set_data(self, req):
        self.data = req.value
        return b''

    def handle_get_modem_status(self, req):
        return b'\x00' * req.length

    def handle_set_event_char(self, req):
        return b''

    def handle_set_error_char(self, req):
        return b''

    def handle_set_latency_timer(self, req):
        self.latency_timer = req.value & 0xff
        return b''

    def handle_get_latency_timer(self, req):
        return struct.pack('B', self.latency_timer)

    def handle_read_ee(self, req):
        return b'\x31\x60'


class USBSaharaInterface(USBInterface):
    name = 'SaharaInterface'

    SAHARA_HELLO_REQ=0x1
    SAHARA_HELLO_RSP=0x2
    SAHARA_READ_DATA=0x3
    SAHARA_END_TRANSFER=0x4
    SAHARA_DONE_REQ=0x5
    SAHARA_DONE_RSP=0x6
    SAHARA_RESET_REQ=0x7
    SAHARA_RESET_RSP=0x8
    SAHARA_MEMORY_DEBUG=0x9
    SAHARA_MEMORY_READ=0xA
    SAHARA_CMD_READY=0xB
    SAHARA_SWITCH_MODE=0xC
    SAHARA_EXECUTE_REQ=0xD
    SAHARA_EXECUTE_RSP=0xE
    SAHARA_EXECUTE_DATA=0xF
    SAHARA_64BIT_MEMORY_DEBUG=0x10
    SAHARA_64BIT_MEMORY_READ=0x11
    SAHARA_64BIT_MEMORY_READ_DATA=0x12

    SAHARA_EXEC_CMD_NOP = 0x00
    SAHARA_EXEC_CMD_SERIAL_NUM_READ = 0x01
    SAHARA_EXEC_CMD_MSM_HW_ID_READ = 0x02
    SAHARA_EXEC_CMD_OEM_PK_HASH_READ = 0x03
    SAHARA_EXEC_CMD_SWITCH_TO_DMSS_DLOAD = 0x04
    SAHARA_EXEC_CMD_SWITCH_TO_STREAM_DLOAD = 0x05
    SAHARA_EXEC_CMD_READ_DEBUG_DATA = 0x06
    SAHARA_EXEC_CMD_GET_SOFTWARE_VERSION_SBL = 0x07
    
    SAHARA_MODE_IMAGE_TX_PENDING = 0x0
    SAHARA_MODE_IMAGE_TX_COMPLETE = 0x1
    SAHARA_MODE_MEMORY_DEBUG = 0x2
    SAHARA_MODE_COMMAND = 0x3

    def __init__(self, app, phy, interface_number):
        self.count=0
        self.timer=None
        self.switch=0
        self.bytestoread=0
        self.bytestotal=0
        self.curoffset=0
        self.buffer=bytes(b'')
        self.loader=bytes(b'')
        self.receive_buffer = bytes(b'')
        super(USBSaharaInterface, self).__init__(
            app=app,
            phy=phy,
            interface_number=interface_number,
            interface_alternate=0,
            interface_class=USBClass.VendorSpecific,
            interface_subclass=0xff,
            interface_protocol=0xff,
            interface_string_index=0,
            endpoints=[
                USBEndpoint(
                    app=app,
                    phy=phy,
                    number=1,
                    direction=USBEndpoint.direction_out,
                    transfer_type=USBEndpoint.transfer_type_bulk,
                    sync_type=USBEndpoint.sync_type_none,
                    usage_type=USBEndpoint.usage_type_data,
                    max_packet_size=0x200,
                    interval=0,
                    handler=self.handle_data_available
                ),
                USBEndpoint(
                    app=app,
                    phy=phy,
                    number=3,
                    direction=USBEndpoint.direction_in,
                    transfer_type=USBEndpoint.transfer_type_bulk,
                    sync_type=USBEndpoint.sync_type_none,
                    usage_type=USBEndpoint.usage_type_data,
                    max_packet_size=0x200,
                    interval=0,
                    handler=self.handle_buffer_available  # at this point, we don't send data to the host
                )
            ],
        )
        #self.txq = Queue()

    def send_data(self, data):
        #print ("TX: ")
        #rec=binascii.hexlify(data)
        #print(rec)
        self.send_on_endpoint(3,data)
        #self.txq.put(data)

    def bytes_as_hex(self, b, delim=" "):
        return delim.join(["%02x" % x for x in b])

    def handle_data_available(self, data):
        global hash
        global hwid
        global serial
        if (self.switch>=2):
            if (len(self.buffer)<self.bytestoread):
                self.buffer+=bytes(data)
                if (len(self.buffer)==self.bytestoread):
                   data=self.buffer
                   self.buffer=bytes(b'')
                   print("Complete RX")
                else:
                   print("Queueing, total: %x of %x" % (len(self.buffer),self.bytestoread))
                   return
            else:
                data=self.buffer
                self.buffer=bytes(b'')
                print("Complete RX")

        #print("RX: ")
        #rec=binascii.hexlify(data)
        #print(rec)
        if len(data) == 0:
            return
        opcode=data[0]
        if (self.switch==0 and opcode==0x3A):
            print("Got download request.")
            init= b"\x7E\x02\x6A\xD3\x7E"
            self.send_data(init)
        elif (self.switch==0):
            print ("Opcode : %x" % opcode)
            if (self.count==0):
                print("Pre init.")
                init = b"\x01\x00\x00\x00\x30\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                self.send_data(init)
                self.count += 1
            elif opcode == self.SAHARA_SWITCH_MODE: #0xC
                print("Got SAHARA_SWITCH_self.")
                request = struct.Struct('<III')
                req = request.unpack(bytes(data))
                '''
                if (req[2]==self.SAHARA_MODE_IMAGE_TX_PENDING): #0
                    request=request
                '''
                if (req[2]==self.SAHARA_MODE_IMAGE_TX_COMPLETE): #1
                    print("SAHARA_MODE_IMAGE_TX_COMPLETE")
                    reply = struct.Struct('<IIIIIIIIIIII')
                    packet = reply.pack(0x01,0x30,0x02,0x01,0x400,0x1,0x0,0x0,0x0,0x0,0x0,0x0)
                    self.send_data(packet)
                elif (req[2]==self.SAHARA_MODE_COMMAND): #3
                    print("SAHARA_MODE_COMMAND")
                    init = b"\x01\x00\x00\x00\x30\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                    self.send_on_endpoint(3, init)
                    #self.count=0
                    #self.switch=0
                '''
                elif (req[2]==self.SAHARA_MODE_MEMORY_DEBUG): #2
                    request=request
                '''
                print("Done SAHARA_SWITCH_self.")

            elif opcode==self.SAHARA_HELLO_RSP: #02
                print("Got SAHARA_HELLO_RSP")
                request = struct.Struct('<IIIIII')
                req = request.unpack(bytes(data[:24]))
                if (req[5]==0x3): #mode
                    packet = struct.pack('<II', 0xB, 0x8)
                    self.send_data(packet)
                elif (req[5]==0x0 or req[5]==0x1): #mode, send loader
                    packet = struct.pack('<IIIII', 0x3, 0x14, 0xD, 0x0, 0x50)
                    self.send_data(packet)
                    self.switch=1
                    self.bytestoread=0x50
                #elif (req[5]==0x1): #mode
                #    packet = struct.pack('<II', 0xB, 0x8)
                #    self.send_data(packet)
                print("Done SAHARA_HELLO_RSP.")
                self.count += 1
            elif opcode == self.SAHARA_EXECUTE_REQ: #0D
                print("Got SAHARA_EXECUTE_REQ")
                request = struct.Struct('<III')
                reply = struct.Struct('<IIII')
                req = request.unpack(bytes(data))
                '''
                if req[2] == self.SAHARA_EXEC_CMD_NOP:
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_NOP, 0x0) #Reply, unk, cmd, replysize
                '''
                if req[2] == self.SAHARA_EXEC_CMD_SERIAL_NUM_READ: #1
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_SERIAL_NUM_READ, 0x4) #Reply 0xE, unk, cmd, replysize
                elif req[2] == self.SAHARA_EXEC_CMD_MSM_HW_ID_READ: #2
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_MSM_HW_ID_READ, 0x18)
                elif req[2] == self.SAHARA_EXEC_CMD_OEM_PK_HASH_READ: #3
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_OEM_PK_HASH_READ, 0x60)
                elif req[2] == self.SAHARA_EXEC_CMD_GET_SOFTWARE_VERSION_SBL: #7
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_GET_SOFTWARE_VERSION_SBL, 0x4)
                '''
                elif req[2] == self.SAHARA_EXEC_CMD_SWITCH_TO_DMSS_DLOAD: #4
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_SWITCH_TO_DMSS_DLOAD, 0x40)
                elif req[2] == self.SAHARA_EXEC_CMD_SWITCH_TO_STREAM_DLOAD: #5
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_SWITCH_TO_STREAM_DLOAD, 0x40)
                elif req[2] == self.SAHARA_EXEC_CMD_READ_DEBUG_DATA: #6
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_READ_DEBUG_DATA, 0x40)
                '''
                
                self.send_data(packet)
                print("Done SAHARA_EXECUTE_REQ.")
            elif opcode == self.SAHARA_EXECUTE_DATA: #0xF
                print("Got SAHARA_EXECUTE_DATA.")
                request = struct.Struct('<III')
                req = request.unpack(bytes(data))
                if req[2] == self.SAHARA_EXEC_CMD_SERIAL_NUM_READ: #1
                    reply = struct.Struct('<I')
                    packet = reply.pack(serial)
                elif req[2] == self.SAHARA_EXEC_CMD_MSM_HW_ID_READ: #2
                    reply = struct.Struct('8s8s8s')
                    packet = reply.pack(hwid, hwid, hwid)
                elif req[2] == self.SAHARA_EXEC_CMD_OEM_PK_HASH_READ: #3
                    reply = struct.Struct('32s32s32s')
                    packet = reply.pack(hash, hash, hash)
                elif req[2] == self.SAHARA_EXEC_CMD_GET_SOFTWARE_VERSION_SBL: #7
                    reply = struct.Struct('<I')
                    packet = reply.pack(sblversion)
                '''
                elif req[2] == self.SAHARA_EXEC_CMD_SWITCH_TO_DMSS_DLOAD: #4
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_SWITCH_TO_DMSS_DLOAD, 0x40)
                elif req[2] == self.SAHARA_EXEC_CMD_SWITCH_TO_STREAM_DLOAD: #5
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_SWITCH_TO_STREAM_DLOAD, 0x40)
                elif req[2] == self.SAHARA_EXEC_CMD_READ_DEBUG_DATA: #6
                    packet = reply.pack(self.SAHARA_EXECUTE_RSP, 0x10, self.SAHARA_EXEC_CMD_READ_DEBUG_DATA, 0x40)
                '''
                self.send_data(packet)
                print("Done SAHARA_EXECUTE_DATA.")
        elif (self.switch==1):
                print("Loader read Init")
                request = struct.Struct('<IIIIIIII')
                req = request.unpack(bytes(data[0:32]))
                if req[0]==0x464c457F:
                    self.elfstart = struct.Struct('<I').unpack(bytes(data[0x20:0x24]))[0]
                    self.bytestotal=0x4000
                    self.switch=2
                    print("ELF Loader detected, ProgHdr start: %x" % self.elfstart)
                else:
                    print("QC Loader detected")
                    self.bytestotal=req[7]
                    self.reallen=req[7]
                    self.switch=3
                print("Reading length: "+hex(self.bytestotal))
                self.curoffset=0x50
                self.loader+=bytes(data)
                packet = struct.pack('<IIIII', 0x3, 0x13, 0xD, self.curoffset, 0x1000)
                self.bytestoread=0x1000
                self.send_data(packet)
        elif (self.switch==2):
                print("ELF read")
                x=self.elfstart
                self.loader+=bytes(data)
                self.bytestotal=0x0
                while (1):
                    start = struct.Struct('<Q').unpack(bytes(self.loader[(x+0x8):(x+0x8+0x8)]))[0]
                    length = struct.Struct('<Q').unpack(bytes(self.loader[(x+0x20):(x+0x20+0x8)]))[0]
                    if (start+length)==0:
                        break
                    self.bytestotal = start+length
                    #print("start : "+hex(start))
                    #print("length : "+hex(length))
                    x+=0x38
                print("Reading length: "+hex(self.bytestotal))
                self.reallen=self.bytestotal
                self.curoffset=0x1050
                self.bytestotal-=(0x1000-0x50)
                self.switch=3
                packet = struct.pack('<IIIII', 0x3, 0x13, 0xD, self.curoffset, 0x1000)
                self.bytestoread=0x1000
                self.send_data(packet)
        elif self.switch==3:
                print("Loader reading")
                self.loader+=bytes(data)
                self.bytestotal-=len(data)
                if (self.bytestotal<=0):
                   packet = struct.pack('<IIII', 0x4, 0x10, 0xD, 0x0)
                   self.send_data(packet)
                   self.switch=0
                   self.bytestoread=0
                   hwidstr=''.join('{:02X}'.format(x) for x in hwid)
                   with open(hwidstr+".bin","wb") as ft:
                        ft.write(self.loader[0:self.reallen])
                        print("We received all loader, stored as: %s" % (hwidstr+".bin"))
                   print("All loader done.")
                else:
                   toread=self.bytestotal
                   if (toread>0x1000):
                       toread=0x1000
                   self.curoffset+=toread
                   packet = struct.pack('<IIIII', 0x3, 0x14, 0xD, self.curoffset, 0x1000)
                   self.bytestoread=toread
                   self.send_data(packet)
                   print("Loader to read : %x" % self.bytestotal)

    def handle_buffer_available(self):
             if self.count==0:
                print("Buffer got called")
                init = b"\x01\x00\x00\x00\x30\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                self.send_on_endpoint(3,init)
                self.count += 1




class USBSaharaDevice(USBDevice):
    name = 'SaharaDevice'

    def __init__(self, app, phy, vid=0x05C6, pid=0x9008, rev=0x0100, **kwargs):
        super(USBSaharaDevice, self).__init__(
            app=app,
            phy=phy,
            device_class=USBClass.Unspecified,
            device_subclass=0,
            protocol_rel_num=0,
            max_packet_size_ep0=0x40,
            vendor_id=0x05C6,
            product_id=0x9008,
            device_rev=0x0100,
            manufacturer_string='Qualcomm CDMA Technologies MSM',
            product_string='QHUSB__BULK',
            serial_number_string='',
            configurations=[
                USBConfiguration(
                    app=app,
                    phy=phy,
                    index=1,
                    string='Sahara',
                    interfaces=[
                        USBSaharaInterface(app, phy, 0)
                    ],
                    attributes=USBConfiguration.ATTR_SELF_POWERED,
                )
            ],
            usb_vendor=USBSaharaVendor(app=app, phy=phy)
        )


usb_device = USBSaharaDevice
