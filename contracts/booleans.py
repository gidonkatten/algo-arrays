from pyteal import *


# This is an example of an array of booleans using bits
def contract():

    array = App.globalGet(Bytes("array"))

    # on_create
    on_create = Seq([
        App.globalPut(
            Bytes("array"),
            Bytes("base16", "0x00000000000000000000000000000000")),  # determines array length (16 bytes so 128 bits)
        Int(1)
    ])

    # on_set_bool
    set_bool_value = Btoi(Txn.application_args[2]) > Int(0)
    set_bool_index = ScratchVar(TealType.uint64)
    set_bool_array_slot = set_bool_index.load() / Int(8)
    set_bool_index_slot = set_bool_index.load() % Int(8)
    on_set_bool = Seq([
        set_bool_index.store(Btoi(Txn.application_args[1])),
        App.globalPut(
            Bytes("array"),
            SetByte(
                array,
                set_bool_array_slot,
                SetBit(
                    GetByte(array, set_bool_array_slot),
                    set_bool_index_slot,
                    set_bool_value
                )
            )
        ),
        Int(1)
    ])

    # on_get_bool
    get_bool_index = ScratchVar(TealType.uint64)
    get_bool_array_slot = get_bool_index.load() / Int(8)
    get_bool_index_slot = get_bool_index.load() % Int(8)
    on_get_bool = Seq([
        get_bool_index.store(Btoi(Txn.application_args[1])),
        GetBit(
            GetByte(array, get_bool_array_slot),
            get_bool_index_slot
        )
    ])

    return Cond(
        [Txn.on_completion() == OnComplete.DeleteApplication, Int(0)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(0)],
        [Txn.on_completion() == OnComplete.CloseOut, Int(0)],
        [Txn.on_completion() == OnComplete.OptIn, Int(0)],
        # On app creation
        [Txn.application_id() == Int(0), on_create],
        # Must be a NoOp transaction
        [Txn.application_args[0] == Bytes("set_bool"), on_set_bool],
        [Txn.application_args[0] == Bytes("get_bool"), on_get_bool]
    )


if __name__ == "__main__":
    print(compileTeal(contract(), Mode.Application, version=4))
