from pyteal import *


# This is an example of an array of integer using bytes
def contract():

    array = App.globalGet(Bytes("array"))

    # on_create
    on_create = Seq([
        App.globalPut(
            Bytes("array"),
            Bytes("base16", "0x00000000000000000000")),  # determines array length (10 bytes)
        Int(1)
    ])

    # on_set_int
    set_int_index = Btoi(Txn.application_args[1])
    set_int_value = Btoi(Txn.application_args[2])
    on_set_int = Seq([
        App.globalPut(
            Bytes("array"),
            SetByte(
                array,
                set_int_index,
                set_int_value
            )
        ),
        Int(1)
    ])

    # on_get_bool
    get_bool_index = Btoi(Txn.application_args[1])
    on_is_int_odd = GetByte(array, get_bool_index) % Int(2)

    # on_is_sum_even
    array_stored = ScratchVar(TealType.bytes)
    total = ScratchVar(TealType.uint64)
    i = ScratchVar(TealType.uint64)
    on_is_sum_odd = Seq([
        array_stored.store(array),
        total.store(Int(0)),
        For(i.store(Int(0)), i.load() < Int(10), i.store(i.load() + Int(1))).Do(
            total.store(total.load() + GetByte(array_stored.load(), i.load()))
        ),
        total.load() % Int(2)
    ])

    return Cond(
        [Txn.on_completion() == OnComplete.DeleteApplication, Int(0)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(0)],
        [Txn.on_completion() == OnComplete.CloseOut, Int(0)],
        [Txn.on_completion() == OnComplete.OptIn, Int(0)],
        # On app creation
        [Txn.application_id() == Int(0), on_create],
        # Must be a NoOp transaction
        [Txn.application_args[0] == Bytes("set_int"), on_set_int],
        [Txn.application_args[0] == Bytes("is_int_odd"), on_is_int_odd],
        [Txn.application_args[0] == Bytes("is_sum_odd"), on_is_sum_odd]
    )


if __name__ == "__main__":
    print(compileTeal(contract(), Mode.Application, version=4))
