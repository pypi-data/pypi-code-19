hidden_output = False

src_glob = './**/*_tf.py'
if hidden_output:
    out_glob = './**/.*.tf.json'
    out_fmt  = '.{}.tf.json'
else:
    out_glob = './**/*.tf.json'
    out_fmt  = '{}.tf.json'
