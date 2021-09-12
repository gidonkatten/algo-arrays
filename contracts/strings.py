from pyteal import *
from util import convert_uint_to_bytes


# This is an example of an array of strings using keys in global state
def contract():

    # on_create
    on_create = Seq([
        App.globalPut(Bytes("length"), Txn.global_num_byte_slices()),
        Int(1)
    ])

    # on_set_string
    set_string_index = Btoi(Txn.application_args[1])
    set_string_value = Txn.application_args[2]
    on_set_string = Seq([
        Assert(set_string_index < App.globalGet(Bytes("length"))),
        App.globalPut(convert_uint_to_bytes(set_string_index), set_string_value),
        Int(1)
    ])

    # on_contains
    searched_string_value = Txn.application_args[1]
    found = ScratchVar(TealType.uint64)
    i = ScratchVar(TealType.uint64)
    length = ScratchVar(TealType.uint64)
    key = ScratchVar(TealType.bytes)
    cmp_string = App.globalGetEx(Int(0), key.load())
    on_contains = Seq([
        found.store(Int(0)),
        length.store(App.globalGet(Bytes("length"))),
        For(i.store(Int(0)), i.load() < length.load(), i.store(i.load() + Int(1))).Do(
            Seq([
                key.store(convert_uint_to_bytes(i.load())),
                cmp_string,
                If(
                    cmp_string.hasValue(),
                    If(
                        cmp_string.value() == searched_string_value,
                        Seq([
                            found.store(Int(1)),
                            Break(),
                        ])
                    )
                )
            ])
        ),
        found.load()
    ])

    return Cond(
        [Txn.on_completion() == OnComplete.DeleteApplication, Int(0)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(0)],
        [Txn.on_completion() == OnComplete.CloseOut, Int(0)],
        [Txn.on_completion() == OnComplete.OptIn, Int(0)],
        # On app creation
        [Txn.application_id() == Int(0), on_create],
        # Must be a NoOp transaction
        [Txn.application_args[0] == Bytes("set_string"), on_set_string],
        [Txn.application_args[0] == Bytes("contains"), on_contains]
    )


if __name__ == "__main__":
    print(compileTeal(contract(), Mode.Application, version=4))
