# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from tornado import ioloop, gen

from tchannel import TChannel, thrift


service = thrift.load(
    path='examples/guide/keyvalue/service.thrift',
    service='benchmark-server',
)


def test_roundtrip(benchmark):
    loop = ioloop.IOLoop.current()

    server = TChannel('benchmark-server')
    server.listen()

    clients = [TChannel('benchmark-client') for _ in range(10)]

    @server.thrift.register(service.KeyValue)
    def getValue(request):
        return 'bar'

    def roundtrip():
        @gen.coroutine
        def doit():
            futures = []
            # 10 clients send 10 requests concurrently
            for client in clients:
                for _ in range(10):
                    futures.append(
                        client.thrift(
                            service.KeyValue.getValue("foo"),
                            hostport=server.hostport,
                        )
                    )
            yield futures

        return loop.run_sync(doit)

    # Establish initial connection
    roundtrip()

    benchmark(roundtrip)
