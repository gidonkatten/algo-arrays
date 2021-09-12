from pyteal import *
from util import convert_uint_to_bytes


# This is an example of an array of booleans using bits
def contract():

    # scratch values
    index = ScratchVar(TealType.uint64)
    shifted_index = ScratchVar(TealType.uint64)
    key = ScratchVar(TealType.uint64)
    key_as_string = ScratchVar(TealType.bytes)
    byte = ScratchVar(TealType.uint64)
    bit = ScratchVar(TealType.uint64)

    # NOTE: This logic can be optimised for opcode cost but left for readability
    store_key_byte_bit = If(
        index.load() < Int(10160),  # if key is 0-9, else key is 10-63
        Seq([
            key.store(index.load() / Int(1016)),
            byte.store((index.load() % Int(1016)) / Int(8)),
            bit.store((index.load() % Int(1016)) % Int(8))
        ]),
        Seq([
            shifted_index.store(index.load() - Int(10160)),
            key.store(Int(10) + (shifted_index.load() / Int(1008))),
            byte.store((index.load() % Int(1008)) / Int(8)),
            bit.store((index.load() % Int(1008)) % Int(8))
        ])
    )

    # The global state value for the given key
    key_has_value = App.globalGetEx(Int(0), key_as_string.load())
    key_value = App.globalGet(key_as_string.load())

    # passed values
    store_index = index.store(Btoi(Txn.application_args[1]))
    bool_value = Btoi(Txn.application_args[2]) > Int(0)

    # initialise global state value with either 127 or 126 bytes depending on key length
    initialise = If(
        Not(key_has_value.hasValue()),
        App.globalPut(
            key_as_string.load(),
            If(
                index.load() < Int(10160),  # if key is 0-9, else key is 10-63
                Bytes("base16", "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"),
                Bytes("base16", "0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
            )
        )
    )

    # set bool
    on_set_bool = Seq([
        App.globalPut(
            key_as_string.load(),
            SetByte(
                key_value,
                byte.load(),
                SetBit(
                    GetByte(key_value, byte.load()),
                    bit.load(),
                    bool_value
                )
            )
        ),
        Int(1)
    ])

    # get bool
    on_get_bool = GetBit(
        GetByte(
            App.globalGet(key_value),
            byte.load()
        ),
        bit.load()
    )

    # set or get bool
    on_set_or_get_bool = Seq([
        # store values to scratch
        store_index,
        store_key_byte_bit,
        key_as_string.store(convert_uint_to_bytes(key.load())),
        key_has_value,
        # lazy initialise
        initialise,
        Cond(
            [Txn.application_args[0] == Bytes("set_bool"), on_set_bool],
            [Txn.application_args[0] == Bytes("get_bool"), on_get_bool]
        )
    ])

    return Cond(
        [Txn.on_completion() == OnComplete.DeleteApplication, Int(0)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(0)],
        [Txn.on_completion() == OnComplete.CloseOut, Int(0)],
        [Txn.on_completion() == OnComplete.OptIn, Int(0)],
        # On app creation
        [Txn.application_id() == Int(0), Int(1)],
        # Must be a NoOp transaction
        [Int(1), on_set_or_get_bool],
    )


if __name__ == "__main__":
    print(compileTeal(contract(), Mode.Application, version=4))
