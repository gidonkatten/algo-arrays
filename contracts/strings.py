from pyteal import *


# This is an example of an array of strings using keys in global state
def contract():

    length = ScratchVar(TealType.uint64)

    # on_create
    array_length = Btoi(Txn.application_args[0])
    i = ScratchVar(TealType.uint64)
    on_create = Seq([
        length.store(array_length),
        App.globalPut(Bytes("length"), length.load()),
        For(i.store(Int(0)), i.load() < length.load(), i.store(i.load() + Int(1))).Do(
            App.globalPut(Itob(i.load()), Bytes(""))
        ),
        Int(1)
    ])

    # on_set_string
    set_bool_index = Btoi(Txn.application_args[1])
    set_string_value = Txn.application_args[2]
    on_set_string = Seq([
        App.globalPut(Itob(set_bool_index), set_string_value),
        Int(1)
    ])

    # on_contains
    searched_string_value = Txn.application_args[1]
    does_contain = ScratchVar(TealType.uint64)
    i = ScratchVar(TealType.uint64)
    on_contains = Seq([
        does_contain.store(Int(0)),
        length.store(array_length),
        For(i.store(Int(0)), i.load() < length.load(), i.store(i.load() + Int(1))).Do(
            If(App.globalGet(Itob(i.load())) == searched_string_value).Then(Seq([
                does_contain.store(Int(1)),
                Break(),
            ]))
        ),
        does_contain.load()
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
