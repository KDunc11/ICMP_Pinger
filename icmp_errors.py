# The following object contains ICMP error types with their corresponding error code and message obtained from
# Sources:
#   => https://www.erg.abdn.ac.uk/users/gorry/course/inet-pages/icmp-code.html#:~:text=Many%20of%20the%20types%20of,%2C%20Time%20Exceeded%20(11).&text=Many%20of%20these%20ICMP%20types%20have%20a%20%22code%22%20field.
#   => http://en.wikipedia.org/wiki/Internet_Control_Message_Protocol#Control_messages

ICMP_CONTROL_MESSAGE = \
    {
        0: {
            0: 'Echo Reply',
        },
        3: {
            0: 'Destination Network Unreachable',
            1: 'Destination Host Unreachable',
            2: 'Destination protocol unreachable',
            3: 'Destination port unreachable',
            4: 'Fragmentation required, and DF flag set',
            5: 'Source route failed',
            6: 'Destination network unknown',
            7: 'Destination host unknown',
            8: 'Source host isolated',
            9: 'Network administratively prohibited',
            10: 'Host administratively prohibited',
            11: 'Network unreachable for TOS',
            12: 'Host unreachable for TOS',
            13: 'Communication administratively prohibited',
            14: 'Host Precedence Violation',
            15: 'Precedence cutoff in effect',
        },
        4: {
            0: 'Source quench',
        },
        5: {
            0: 'Redirect Datagram for the Network',
            1: 'Redirect Datagram for the Host',
            2: 'Redirect Datagram for the TOS & network',
            3: 'Redirect Datagram for the TOS & host',
        },
        8: {
            0: 'Echo request',
        },
        9: {
            0: 'Router Advertisement',
        },
        10: {
            0: 'Router discovery/selection/solicitation',
         },
        11: {
            0: 'TTL expired in transit',
            1: 'Fragment reassembly time exceeded',
         },
        12: {
            0: 'Pointer indicates the error',
            1: 'Missing a required option',
            2: 'Bad length',
         },
        13: {
            0: 'Timestamp',
        },
        14: {
            0: 'Timestamp reply',
        },
}